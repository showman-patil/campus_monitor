from django.contrib import admin
from .models import (
	Entity, TimelineEvent, Prediction, Alert,
	Identifier, SwipeLog, WifiLog, Booking, LibraryCheckout, Note, FaceEmbedding,
	ResolutionLink, DataProvenance
)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
	list_display = ('name', 'entity_type', 'last_seen', 'status', 'confidence')
	search_fields = ('name', 'entity_type')
	list_filter = ('entity_type', 'status')


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
	list_display = ('timestamp', 'entity', 'event_type', 'location')
	search_fields = ('event_type', 'description', 'location')
	list_filter = ('event_type',)


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
	list_display = ('entity', 'predicted_time', 'predicted_location', 'score', 'model_name')
	search_fields = ('model_name',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
	list_display = ('entity_name', 'alert_type', 'severity', 'status', 'created_at')
	search_fields = ('entity_name', 'alert_type')
	list_filter = ('status', 'severity')


@admin.register(Identifier)
class IdentifierAdmin(admin.ModelAdmin):
	list_display = ('id_type', 'id_value', 'entity', 'source', 'confidence')
	search_fields = ('id_value', 'entity__name', 'source')


@admin.register(SwipeLog)
class SwipeLogAdmin(admin.ModelAdmin):
	list_display = ('card_id', 'location', 'timestamp')
	search_fields = ('card_id', 'location')
	list_filter = ('location',)


@admin.register(WifiLog)
class WifiLogAdmin(admin.ModelAdmin):
	list_display = ('device_hash', 'ap_id', 'timestamp', 'rssi')
	search_fields = ('device_hash', 'ap_id')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ('resource', 'entity', 'start', 'end')
	search_fields = ('resource', 'entity__name')


@admin.register(LibraryCheckout)
class LibraryCheckoutAdmin(admin.ModelAdmin):
	list_display = ('item', 'entity', 'checkout_time', 'due_time')
	search_fields = ('item', 'entity__name')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
	list_display = ('source', 'entity', 'timestamp')
	search_fields = ('text', 'source')


@admin.register(FaceEmbedding)
class FaceEmbeddingAdmin(admin.ModelAdmin):
	list_display = ('entity', 'source', 'timestamp', 'confidence')
	search_fields = ('entity__name', 'source')


@admin.register(ResolutionLink)
class ResolutionLinkAdmin(admin.ModelAdmin):
	list_display = ('left_type', 'left_value', 'right_type', 'right_value', 'confidence')
	search_fields = ('left_value', 'right_value')


@admin.register(DataProvenance)
class DataProvenanceAdmin(admin.ModelAdmin):
	list_display = ('source', 'record_type', 'record_id', 'imported_at')
	search_fields = ('source', 'record_id')
