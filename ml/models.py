from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import User




class UserInteraction(models.Model):
    """Track user interactions for collaborative filtering"""

    INTERACTION_TYPES = [
        ('VIEW', 'Viewed'),
        ('SEARCH', 'Searched'),
        ('BOOKMARK', 'Bookmarked'),
        ('BOOK', 'Booked'),
        ('COMPLETE', 'Completed'),
        ('REVIEW', 'Reviewed'),
        ('CANCEL', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)

    # Generic relation to any model (Service, Professional, ServiceCategory)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Context data
    session_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['created_at']),
        ]