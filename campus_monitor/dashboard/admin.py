from django.contrib import admin
from .models import Entity, TimelineEvent, Prediction, Alert


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
