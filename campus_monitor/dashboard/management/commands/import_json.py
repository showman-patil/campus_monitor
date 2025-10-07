from django.core.management.base import BaseCommand
import os
import json
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime

from campus_monitor.dashboard.models import Entity, TimelineEvent, Prediction, Alert

class Command(BaseCommand):
    help = 'Import sample JSON data into the dashboard models'

    def handle(self, *args, **options):
        base = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        base = os.path.abspath(base)

        def parse_datetime(value):
            """Try to parse a datetime from various common formats. Returns aware datetime or None."""
            if not value:
                return None
            if isinstance(value, datetime):
                return timezone.make_aware(value) if timezone.is_naive(value) else value
            # try ISO
            try:
                dt = datetime.fromisoformat(value)
                return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
            except Exception:
                pass
            # try common time-only format like '09:10' -> attach today's date
            try:
                t = datetime.strptime(value, '%H:%M')
                today = timezone.now().date()
                dt = datetime.combine(today, t.time())
                return timezone.make_aware(dt)
            except Exception:
                pass
            # try full datetime with common separators
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S', '%d-%m-%Y %H:%M'):
                try:
                    dt = datetime.strptime(value, fmt)
                    return timezone.make_aware(dt)
                except Exception:
                    continue
            return None

        # entities
        entities_path = os.path.join(base, 'entities.json')
        if os.path.exists(entities_path):
            with open(entities_path, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                name = item.get('entity') or item.get('name')
                etype = item.get('type')
                last_seen = parse_datetime(item.get('last_seen'))
                status = item.get('status')
                confidence = None
                try:
                    confidence = float(item.get('confidence') or item.get('score') or 0.0)
                except Exception:
                    pass
                metadata = item.copy()
                Entity.objects.update_or_create(
                    name=name,
                    defaults={
                        'entity_type': etype,
                        'last_seen': last_seen,
                        'status': status or '',
                        'confidence': confidence,
                        'metadata': metadata,
                    }
                )
            self.stdout.write(self.style.SUCCESS('Imported entities.json'))

        # timeline
        timeline_path = os.path.join(base, 'timeline.json')
        if os.path.exists(timeline_path):
            with open(timeline_path, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                # assume timeline items have {time, event, entity}
                ts = parse_datetime(item.get('time') or item.get('timestamp'))
                ev = item.get('event') or item.get('description')
                name = item.get('entity')
                if name:
                    entity = Entity.objects.filter(name=name).first()
                else:
                    entity = None
                TimelineEvent.objects.create(
                    entity=entity,
                    timestamp=ts or timezone.now(),
                    event_type=ev or '',
                    description=item.get('description') or '',
                    location=item.get('location') or '',
                    data=item,
                )
            self.stdout.write(self.style.SUCCESS('Imported timeline.json'))

        # predictions
        predictions_path = os.path.join(base, 'predictions.json')
        if os.path.exists(predictions_path):
            with open(predictions_path, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                if isinstance(item, str):
                    name = item
                    item = {}
                else:
                    name = item.get('entity')
                entity = Entity.objects.filter(name=name).first() if name else None
                predicted_time = parse_datetime(item.get('predicted_time') or item.get('time'))
                Prediction.objects.update_or_create(
                    entity=entity,
                    predicted_time=predicted_time,
                    defaults={
                        'predicted_location': item.get('predicted_location') or item.get('location') or '',
                        'score': item.get('confidence') or item.get('score') or 0.0,
                        'model_name': item.get('model') or '',
                        'payload': item,
                    }
                )
            self.stdout.write(self.style.SUCCESS('Imported predictions.json'))

        # alerts
        alerts_path = os.path.join(base, 'alerts.json')
        if os.path.exists(alerts_path):
            with open(alerts_path, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                if isinstance(item, str):
                    name = item
                    item = {}
                else:
                    name = item.get('entity')
                entity = Entity.objects.filter(name=name).first() if name else None
                Alert.objects.create(
                    entity=entity,
                    entity_name=name or (entity.name if entity else ''),
                    alert_type=item.get('type') or 'Alert',
                    message=item.get('status') or item.get('message') or '',
                    severity=1,
                    status='open',
                    extra=item,
                )
            self.stdout.write(self.style.SUCCESS('Imported alerts.json'))

        # post-process: generate inactivity alerts for entities not seen >12 hours
        cutoff = timezone.now() - timedelta(hours=12)
        inactive = Entity.objects.filter(last_seen__lt=cutoff)
        for ent in inactive:
            Alert.objects.get_or_create(
                entity=ent,
                alert_type='Inactive',
                defaults={
                    'entity_name': ent.name,
                    'message': f'No logs for >12h (last_seen {ent.last_seen})',
                    'severity': 2,
                    'status': 'open',
                    'extra': {},
                }
            )
        self.stdout.write(self.style.SUCCESS('Post-processed inactivity alerts'))
