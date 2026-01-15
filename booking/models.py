from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from professional.models import Professional
from customer.models import CustomerProfile
from service.models import Service

User = get_user_model()


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),           # Customer created, awaiting professional
        ('ACCEPTED', 'Accepted'),         # Professional accepted
        ('REJECTED', 'Rejected'),         # Professional rejected
        ('IN_PROGRESS', 'In Progress'),   # Work started
        ('COMPLETED', 'Completed'),       # Work finished
        ('CANCELLED', 'Cancelled'),       # Cancelled by either party
    ]

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='booking_requests'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()

    # Location (can differ from customer profile)
    address = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    # Details
    special_instructions = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )  # For PER_UNIT pricing

    # Pricing
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    rejection_reason = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['professional', 'status']),
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.service.title} ({self.status})"

