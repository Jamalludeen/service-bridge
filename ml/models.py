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


class ServiceSimilarity(models.Model):
    """Pre-computed service similarity scores"""

    service_a = models.ForeignKey(
        'service.Service',
        on_delete=models.CASCADE,
        related_name='similarities_as_a'
    )
    service_b = models.ForeignKey(
        'service.Service',
        on_delete=models.CASCADE,
        related_name='similarities_as_b'
    )
    similarity_score = models.FloatField()  # 0.0 to 1.0

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['service_a', 'service_b']
        indexes = [
            models.Index(fields=['service_a', 'similarity_score']),
        ]


class ProfessionalScore(models.Model):
    """ML-computed professional quality scores"""

    professional = models.OneToOneField(
        'professional.Professional',
        on_delete=models.CASCADE,
        related_name='ml_score'
    )

    # Component scores (0.0 to 1.0)
    rating_score = models.FloatField(default=0.5)
    completion_rate_score = models.FloatField(default=0.5)
    response_time_score = models.FloatField(default=0.5)
    experience_score = models.FloatField(default=0.5)
    consistency_score = models.FloatField(default=0.5)

    # Final composite score
    overall_score = models.FloatField(default=0.5)

    # Metadata
    bookings_analyzed = models.IntegerField(default=0)
    last_computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-overall_score']


class CustomerPreference(models.Model):
    """Learned customer preferences"""

    customer = models.OneToOneField(
        'customer.CustomerProfile',
        on_delete=models.CASCADE,
        related_name='ml_preferences'
    )

    # Learned preferences (stored as JSON for flexibility)
    preferred_categories = models.JSONField(default=list)  # [{"id": 1, "weight": 0.8}, ...]
    preferred_price_range = models.JSONField(default=dict)  # {"min": 100, "max": 500}
    preferred_times = models.JSONField(default=list)  # ["morning", "afternoon"]
    preferred_days = models.JSONField(default=list)  # ["saturday", "sunday"]

    # Derived features
    avg_booking_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    booking_frequency_days = models.FloatField(null=True, blank=True)

    last_computed_at = models.DateTimeField(auto_now=True)


class RecommendationLog(models.Model):
    """Track recommendations for A/B testing and improvement"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendation_logs'
    )
    recommendation_type = models.CharField(max_length=50)

    # What was recommended
    recommended_items = models.JSONField()  # List of IDs

    # What was clicked/selected
    selected_item_id = models.IntegerField(null=True, blank=True)

    # Algorithm metadata
    algorithm_version = models.CharField(max_length=50)
    context = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
