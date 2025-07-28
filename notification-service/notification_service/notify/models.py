from django.db import models

# Create your models here.
import uuid
from django.db import models


class NotificationType(models.TextChoices):
    REQUEST_ACCEPTED = 'request_accepted'
    REQUEST_REJECTED = 'request_rejected'
    NEW_MEMBER_ADDED = 'new_member_added'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.IntegerField()

    team_application_id = models.IntegerField()

    message = models.TextField()

    type = models.CharField(max_length=50, choices=NotificationType.choices)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['is_read']),
        ]