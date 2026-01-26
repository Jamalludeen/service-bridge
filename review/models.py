from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db import models

from professional.models import Professional
from booking.models import Booking

User = get_user_model()


class Review(models.Model):
    """Customer review for a completed booking"""

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review'
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )

    # Rating & Content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True)

    # Moderation
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['professional', 'is_approved']),
            models.Index(fields=['customer']),
            models.Index(fields=['rating']),
        ]
        # Ensure one review per booking
        constraints = [
            models.UniqueConstraint(
                fields=['booking'],
                name='one_review_per_booking'
            )
        ]

    def __str__(self):
        return f"Review by {self.customer.username} for {self.professional.user.username} - {self.rating}⭐"

class ReviewResponse(models.Model):
    """Professional's response to a customer review"""

    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='response'
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='review_responses'
    )
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Response by {self.professional.user.username} to review #{self.review.id}"

