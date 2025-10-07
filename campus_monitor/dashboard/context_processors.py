from django.utils import timezone

try:
    from .models import TimelineEvent
except Exception:
    TimelineEvent = None


def server_date(request):
    """Context processor that makes a server-side date available in all templates.

    Uses the latest TimelineEvent.timestamp if the model/table exists and has
    data; otherwise falls back to timezone.now().
    """
    server_dt = timezone.now()
    if TimelineEvent is not None:
        try:
            latest = TimelineEvent.objects.order_by('-timestamp').first()
            if latest and latest.timestamp:
                server_dt = latest.timestamp
        except Exception:
            # If migrations haven't been run or table doesn't exist yet, ignore.
            pass
    # determine if the current user should be treated as staff
    user_is_staff = False
    try:
        if request.user.is_authenticated:
            prof = getattr(request.user, 'profile', None)
            if prof and getattr(prof, 'role', None) in ('Staff', 'Admin'):
                user_is_staff = True
            else:
                user_is_staff = getattr(request.user, 'is_staff', False)
    except Exception:
        user_is_staff = getattr(request.user, 'is_staff', False)

    return {'server_date': server_dt, 'user_is_staff': user_is_staff}
