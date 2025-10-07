from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import TimelineEvent, Entity, Prediction, Alert
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout

def index(request):
    # Use the most recent timeline event timestamp as the "date" to show
    # in the index page. If no timeline events exist, fall back to now.
    latest_event = TimelineEvent.objects.order_by('-timestamp').first()
    server_date = latest_event.timestamp if latest_event else timezone.now()
    return render(request, 'dashboard/index.html', {'server_date': server_date})

def search_page(request):
    # Provide initial payload composed only from the Entity model.
    # Only include entities that have BOTH a metadata.source and a last_seen
    # (i.e. "full information"). If the current user is staff, restrict
    # the results to entity_type == 'Student' per request.
    qs = Entity.objects.all()
    # filter for full info
    good_entities = []
    # treat users with profile.role in ('Staff','Admin') as staff as well
    user_is_staff = False
    if request.user.is_authenticated:
        try:
            role = getattr(request.user, 'profile', None)
            if role and getattr(request.user.profile, 'role', None) in ('Staff', 'Admin'):
                user_is_staff = True
        except Exception:
            user_is_staff = getattr(request.user, 'is_staff', False)
    if not user_is_staff:
        user_is_staff = getattr(request.user, 'is_staff', False)

    for e in qs.order_by('-last_seen'):
        try:
            has_source = False
            if e.metadata and isinstance(e.metadata, dict):
                if e.metadata.get('source'):
                    has_source = True
        except Exception:
            has_source = False
        if not has_source or not e.last_seen:
            continue
        # if staff user, only include Students
        if user_is_staff:
            if (e.entity_type or '').lower() != 'student':
                continue

        good_entities.append(e)

    initial = []
    for e in good_entities[:200]:
        initial.append({
            'name': e.name,
            'type': e.entity_type or 'Entity',
            'source': e.metadata.get('source') if (e.metadata and isinstance(e.metadata, dict)) else 'db',
            'timestamp': e.last_seen.isoformat() if e.last_seen else None,
            'confidence': e.confidence if e.confidence is not None else 0.0,
        })

    import json
    return render(request, 'dashboard/search.html', {'initial_entities': json.dumps(initial)})


def add_entity_view(request):
    """Simple page to add an Entity. Accessible only to staff users.

    Uses raw POST fields: name, entity_type, last_seen (ISO datetime), status,
    confidence, metadata (JSON string).
    """
    # allow users whose Profile.role is Staff/Admin, or Django is_staff flag
    user_is_staff = False
    if request.user.is_authenticated:
        try:
            if getattr(request.user, 'profile', None) and request.user.profile.role in ('Staff', 'Admin'):
                user_is_staff = True
        except Exception:
            user_is_staff = False
    if not user_is_staff:
        user_is_staff = getattr(request.user, 'is_staff', False)

    if not request.user.is_authenticated or not user_is_staff:
        # redirect anonymous or non-staff to login
        messages.error(request, 'You must be an admin/staff to add entities.')
        return redirect('login')

    errors = {}
    initial = {}
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        entity_type = request.POST.get('entity_type', '').strip()
        last_seen = request.POST.get('last_seen', '').strip()
        status = request.POST.get('status', '').strip()
        confidence = request.POST.get('confidence', '').strip()
        metadata_raw = request.POST.get('metadata', '').strip()

        initial = {'name': name, 'entity_type': entity_type, 'last_seen': last_seen, 'status': status, 'confidence': confidence, 'metadata': metadata_raw}

        if not name:
            errors['name'] = 'Name is required.'

        # parse last_seen
        from django.utils.dateparse import parse_datetime
        ls_dt = None
        if last_seen:
            ls_dt = parse_datetime(last_seen)
            if ls_dt is None:
                errors['last_seen'] = 'Invalid datetime. Use ISO format: YYYY-MM-DDTHH:MM'

        # parse confidence
        conf_val = None
        if confidence:
            try:
                conf_val = float(confidence)
            except Exception:
                errors['confidence'] = 'Invalid number for confidence.'

        # parse metadata JSON
        meta = None
        if metadata_raw:
            import json
            try:
                meta = json.loads(metadata_raw)
            except Exception:
                errors['metadata'] = 'Invalid JSON for metadata.'

        if not errors:
            ent = Entity(
                name=name,
                entity_type=entity_type,
                last_seen=ls_dt,
                status=status,
                confidence=conf_val,
                metadata=meta,
            )
            ent.save()
            messages.success(request, f'Entity "{ent.name}" created.')
            return redirect('search')

    return render(request, 'dashboard/add_entity.html', {'errors': errors, 'initial': initial})
    # If User model isn't available for some reason, ignore users.
    pass


def timeline_page(request):
    return render(request, 'dashboard/timeline.html')

def predict_page(request):
    return render(request, 'dashboard/predict.html')

def alerts_page(request):
    return render(request, 'dashboard/alerts.html')


def signup_view(request):
    """Handle signup using raw POST inputs from an HTML form (no Django form class).

    Returns inline errors to template for display.
    """
    errors = {}
    initial = {'username': ''}
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        initial['username'] = username

        # Basic validation
        if not username:
            errors['username'] = 'Username is required.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username already taken.'

        if not password1:
            errors['password1'] = 'Password is required.'
        elif len(password1) < 8:
            errors['password1'] = 'Password must be at least 8 characters.'

        if password1 != password2:
            errors['password2'] = 'Passwords do not match.'

        if not errors:
            user = User.objects.create_user(username=username, password=password1)
            user.save()
            # automatically authenticate and log the user in
            user = authenticate(request, username=username, password=password1)
            if user:
                auth_login(request, user)
                messages.success(request, 'Welcome! Your account was created and you are now logged in.')
                return redirect('index')
            else:
                messages.success(request, 'Account created successfully. Please log in.')
                return redirect('login')

    return render(request, 'dashboard/signup.html', {'errors': errors, 'initial': initial})


def login_view(request):
    """Custom login view that accepts POSTed username/password and logs user in."""
    errors = {}
    username = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('index')
        else:
            errors['all'] = 'Invalid username or password.'
            # Helpful debug hint when running in DEBUG mode
            try:
                from django.conf import settings
                if getattr(settings, 'DEBUG', False):
                    errors['debug'] = f"POST received: {request.method == 'POST'}, username present: {bool(request.POST.get('username'))}"
            except Exception:
                pass

    return render(request, 'dashboard/login.html', {'errors': errors, 'username': username})

def api_search(request):
    """Return entities from the database in the same shape the frontend expects.

    Frontend fields: name, type, source, timestamp, confidence
    """
    qs = Entity.objects.all().order_by('-last_seen')
    result = []
    for e in qs:
        source = None
        if e.metadata and isinstance(e.metadata, dict):
            source = e.metadata.get('source')
        result.append({
            'name': e.name,
            'type': e.entity_type or '',
            'source': source or '',
            'timestamp': e.last_seen.isoformat() if e.last_seen else None,
            'confidence': e.confidence if e.confidence is not None else 0.0,
        })
    return JsonResponse(result, safe=False)

def api_timeline(request):
    """Return timeline events from the DB in a simplified shape for the UI.

    Frontend expects items with keys like: icon, event, time
    """
    qs = TimelineEvent.objects.select_related('entity').order_by('-timestamp')[:100]
    result = []
    for ev in qs:
        name = ev.entity.name if ev.entity else None
        event_text = ev.event_type or ev.description or 'Event'
        # time as human friendly string for the UI
        time_str = ev.timestamp.isoformat() if ev.timestamp else ''
        result.append({
            'icon': '🕒',
            'event': event_text,
            'time': time_str,
            'entity': name,
            'location': ev.location or '',
            'description': ev.description or '',
        })
    return JsonResponse(result, safe=False)

def api_predict(request):
    # Return the most recent prediction if available, else an empty object
    p = Prediction.objects.select_related('entity').order_by('-created_at').first()
    if not p:
        return JsonResponse({}, safe=False)

    return JsonResponse({
        'entity': p.entity.name if p.entity else p.payload.get('entity') if p.payload else '',
        'predicted_location': p.predicted_location or (p.payload.get('predicted_location') if p.payload else ''),
        'confidence': p.score if p.score is not None else 0.0,
        'explanation': p.payload.get('explanation') if p.payload and isinstance(p.payload, dict) else p.model_name or '',
    }, safe=False)

def api_alerts(request):
    qs = Alert.objects.select_related('entity').order_by('-created_at')
    result = []
    for a in qs:
        ent = a.entity
        last_seen = None
        ent_type = ''
        if ent:
            last_seen = ent.last_seen.isoformat() if ent.last_seen else None
            ent_type = ent.entity_type or ''
        else:
            # try to parse last_seen from extra or created_at
            last_seen = a.extra.get('last_seen') if a.extra and isinstance(a.extra, dict) else (a.created_at.isoformat())

        result.append({
            'entity': ent.name if ent else a.entity_name,
            'type': ent_type,
            'last_seen': last_seen,
            'status': a.status,
            'severity': a.severity,
            'message': a.message,
        })
    return JsonResponse(result, safe=False)
