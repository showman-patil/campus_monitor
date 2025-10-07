from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

# Domain models for the dashboard app. These map to the JSON fixtures used
# by the sample views (entities, timeline, predictions, alerts) and provide
# a foundation for storing them in the database instead of static files.

class Entity(models.Model):
	"""Represents an identified campus entity (person, asset, device, etc.).

	Fields are intentionally flexible: metadata is a JSON blob for extra
	attributes coming from various sensor feeds.
	"""

	name = models.CharField(max_length=200)
	entity_type = models.CharField(max_length=100, blank=True)
	last_seen = models.DateTimeField(null=True, blank=True)
	status = models.CharField(max_length=100, blank=True)
	confidence = models.FloatField(null=True, blank=True)
	metadata = models.JSONField(blank=True, null=True)

	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-last_seen', '-updated_at']

	def __str__(self):
		return f"{self.name} ({self.entity_type})" if self.entity_type else self.name


class TimelineEvent(models.Model):
	"""A timestamped event related to an entity.

	The app's timeline view can display these events in chronological order.
	"""

	entity = models.ForeignKey(Entity, related_name='events', on_delete=models.SET_NULL, null=True, blank=True)
	timestamp = models.DateTimeField()
	event_type = models.CharField(max_length=150, blank=True)
	description = models.TextField(blank=True)
	location = models.CharField(max_length=200, blank=True)
	data = models.JSONField(blank=True, null=True)

	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ['-timestamp']

	def __str__(self):
		who = self.entity.name if self.entity else 'Unknown'
		return f"{self.timestamp.isoformat()} — {who} — {self.event_type}"


class Prediction(models.Model):
	"""Predicted future information (location, status, etc.) for an entity.

	Predictions may come from an ML model; store model metadata and payload
	so predictions are auditable and traceable.
	"""

	entity = models.ForeignKey(Entity, related_name='predictions', on_delete=models.SET_NULL, null=True, blank=True)
	predicted_time = models.DateTimeField(null=True, blank=True)
	predicted_location = models.CharField(max_length=200, blank=True)
	score = models.FloatField(null=True, blank=True)
	model_name = models.CharField(max_length=200, blank=True)
	payload = models.JSONField(blank=True, null=True)

	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		target = self.entity.name if self.entity else 'Unknown'
		return f"Prediction for {target} @ {self.predicted_time or 'N/A'} ({self.score})"


class Alert(models.Model):
	"""Security or monitoring alerts related to entities or assets.

	Alerts can be generated from rules, analytics, or ML. Status tracks
	whether the alert is open/resolved.
	"""

	STATUS_CHOICES = [
		('open', 'Open'),
		('ack', 'Acknowledged'),
		('resolved', 'Resolved'),
	]

	entity = models.ForeignKey(Entity, related_name='alerts', on_delete=models.SET_NULL, null=True, blank=True)
	entity_name = models.CharField(max_length=200, blank=True)
	alert_type = models.CharField(max_length=150, blank=True)
	message = models.TextField(blank=True)
	severity = models.IntegerField(null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
	extra = models.JSONField(blank=True, null=True)

	created_at = models.DateTimeField(default=timezone.now)
	resolved_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-created_at']

	def save(self, *args, **kwargs):
		# ensure entity_name is populated for easier queries when entity FK is missing
		if not self.entity_name and self.entity:
			self.entity_name = self.entity.name
		super().save(*args, **kwargs)

	def __str__(self):
		return f"[{self.get_status_display()}] {self.entity_name or (self.entity.name if self.entity else 'Unknown')} - {self.alert_type}"


# Simple profile attached to Django's user model so we can store a role
# (Student, Staff, Admin) without changing the project's AUTH_USER_MODEL.
class Profile(models.Model):
	ROLE_CHOICES = [
		('Student', 'Student'),
		('Staff', 'Staff'),
		('Admin', 'Admin'),
	]

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')

	def __str__(self):
		return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, **kwargs):
	"""Ensure a Profile exists for every user. Default role is Student."""
	if created:
		Profile.objects.create(user=instance)


# --- Extended schema for the Saptang Labs challenge ---

class Identifier(models.Model):
	"""Cross-source identifiers for an Entity (card_id, email, student_id, device_hash, face_id, etc.)"""
	entity = models.ForeignKey(Entity, related_name='identifiers', on_delete=models.CASCADE)
	id_type = models.CharField(max_length=100)  # e.g., 'card_id', 'email', 'device_hash', 'face_id'
	id_value = models.CharField(max_length=500, db_index=True)
	source = models.CharField(max_length=200, blank=True)  # which system provided this id
	confidence = models.FloatField(null=True, blank=True)
	metadata = models.JSONField(blank=True, null=True)

	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = (('id_type', 'id_value'),)

	def __str__(self):
		return f"{self.id_type}:{self.id_value} -> {self.entity.name}"


class SwipeLog(models.Model):
	card_id = models.CharField(max_length=200, db_index=True)
	location = models.CharField(max_length=200)
	timestamp = models.DateTimeField()
	raw = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"Swipe {self.card_id} @ {self.location} @ {self.timestamp.isoformat()}"


class WifiLog(models.Model):
	device_hash = models.CharField(max_length=200, db_index=True)
	ap_id = models.CharField(max_length=200)
	timestamp = models.DateTimeField()
	rssi = models.IntegerField(null=True, blank=True)
	raw = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"WiFi {self.device_hash} @ {self.ap_id} @ {self.timestamp.isoformat()}"


class Booking(models.Model):
	entity = models.ForeignKey(Entity, related_name='bookings', on_delete=models.SET_NULL, null=True, blank=True)
	resource = models.CharField(max_length=200)
	start = models.DateTimeField()
	end = models.DateTimeField()
	metadata = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		who = self.entity.name if self.entity else 'Unknown'
		return f"Booking {self.resource} for {who} {self.start.isoformat()}"


class LibraryCheckout(models.Model):
	entity = models.ForeignKey(Entity, related_name='checkouts', on_delete=models.SET_NULL, null=True, blank=True)
	item = models.CharField(max_length=300)
	checkout_time = models.DateTimeField()
	due_time = models.DateTimeField(null=True, blank=True)
	metadata = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		who = self.entity.name if self.entity else 'Unknown'
		return f"Checkout {self.item} by {who} @ {self.checkout_time.isoformat()}"


class Note(models.Model):
	"""Free-text notes from helpdesk, event RSVPs, etc."""
	entity = models.ForeignKey(Entity, related_name='notes', on_delete=models.SET_NULL, null=True, blank=True)
	source = models.CharField(max_length=200, blank=True)
	timestamp = models.DateTimeField()
	text = models.TextField()
	metadata = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"Note @{self.timestamp.isoformat()} ({self.source})"


class FaceEmbedding(models.Model):
	"""Store face embeddings or image references for face-based linking."""
	entity = models.ForeignKey(Entity, related_name='face_embeddings', on_delete=models.SET_NULL, null=True, blank=True)
	embedding = models.BinaryField(blank=True, null=True)  # store raw bytes if needed
	vector = models.JSONField(blank=True, null=True)  # or a JSON list of floats
	image_ref = models.CharField(max_length=500, blank=True)
	source = models.CharField(max_length=200, blank=True)
	confidence = models.FloatField(null=True, blank=True)
	timestamp = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"FaceEmb for {self.entity.name if self.entity else 'Unknown'} @ {self.timestamp}"


class ResolutionLink(models.Model):
	"""A link that indicates two identifiers/entities are considered the same with a confidence score and provenance."""
	left_type = models.CharField(max_length=100)
	left_value = models.CharField(max_length=500)
	right_type = models.CharField(max_length=100)
	right_value = models.CharField(max_length=500)
	confidence = models.FloatField(null=True, blank=True)
	evidence = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"Link {self.left_type}:{self.left_value} ⇄ {self.right_type}:{self.right_value} ({self.confidence})"


class DataProvenance(models.Model):
	"""Track provenance for imported records so predictions and links can be explained."""
	source = models.CharField(max_length=200)
	record_type = models.CharField(max_length=200)
	record_id = models.CharField(max_length=400)
	raw = models.JSONField(blank=True, null=True)
	imported_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.source} {self.record_type}:{self.record_id}"


