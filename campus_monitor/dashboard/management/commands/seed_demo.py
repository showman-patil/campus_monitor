from django.core.management.base import BaseCommand
from django.utils import timezone
from campus_monitor.dashboard.models import Entity, Identifier, SwipeLog, WifiLog, Booking, LibraryCheckout, Note, FaceEmbedding, ResolutionLink, DataProvenance

class Command(BaseCommand):
    help = 'Seed the database with demo entities and logs for the challenge'

    def handle(self, *args, **options):
        now = timezone.now()

        # create a few demo entities
        e1, _ = Entity.objects.get_or_create(name='Rahul Patel', defaults={'entity_type': 'Student', 'last_seen': now, 'confidence': 0.92})
        e2, _ = Entity.objects.get_or_create(name='John Doe', defaults={'entity_type': 'Staff', 'last_seen': now - timezone.timedelta(hours=2), 'confidence': 0.88})
        e3, _ = Entity.objects.get_or_create(name='Laptop-124', defaults={'entity_type': 'Asset', 'last_seen': now - timezone.timedelta(days=1), 'confidence': 0.75})

        # identifiers
        Identifier.objects.get_or_create(entity=e1, id_type='email', id_value='rahul.patel@example.edu', defaults={'source': 'profiles'})
        Identifier.objects.get_or_create(entity=e1, id_type='student_id', id_value='S12345', defaults={'source': 'sis'})
        Identifier.objects.get_or_create(entity=e2, id_type='email', id_value='j.doe@example.edu', defaults={'source': 'hr'})
        Identifier.objects.get_or_create(entity=e3, id_type='asset_tag', id_value='Laptop-124', defaults={'source': 'inventory'})

        # logs
        SwipeLog.objects.create(card_id='CARD-1001', location='Library Entrance', timestamp=now - timezone.timedelta(hours=1), raw={'note': 'demo swipe'})
        WifiLog.objects.create(device_hash='devhash-xyz', ap_id='AP_23', timestamp=now - timezone.timedelta(minutes=30), rssi=-45)

        Booking.objects.create(entity=e1, resource='Lab 3', start=now.replace(hour=9, minute=0), end=now.replace(hour=11, minute=0))
        LibraryCheckout.objects.create(entity=e1, item='Intro to Algorithms', checkout_time=now - timezone.timedelta(days=2), due_time=now + timezone.timedelta(days=12))
        Note.objects.create(entity=e1, source='helpdesk', timestamp=now - timezone.timedelta(days=1), text='Reported lost access card', metadata={'tags': ['helpdesk']})

        # face embedding (store vector as small list for demo)
        FaceEmbedding.objects.create(entity=e1, vector=[0.1, 0.2, 0.3], source='face_system', confidence=0.85, timestamp=now - timezone.timedelta(hours=3))

        # resolution link example
        ResolutionLink.objects.create(left_type='student_id', left_value='S12345', right_type='email', right_value='rahul.patel@example.edu', confidence=0.98, evidence={'method': 'seed'})

        DataProvenance.objects.create(source='seed', record_type='demo', record_id='seed-run-1', raw={'created': True})

        self.stdout.write(self.style.SUCCESS('Seeded demo entities and logs'))
