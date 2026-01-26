from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal
import uuid

from booking.models import Booking
from core.models import User


class Payment(models.Model):
    """Payment model linked to a booking"""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),           # Payment initiated, waiting for funds
        ('HELD', 'Held in Escrow'),       # Funds received and held
        ('RELEASED', 'Released'),          # Released to professional
        ('REFUNDED', 'Refunded'),          # Returned to customer
        ('FAILED', 'Failed'),              # Payment failed
        ('CANCELLED', 'Cancelled'),        # Payment cancelled
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash on Delivery'),
        ('MOBILE_MONEY', 'Mobile Money'),      # M-Paisa, etc.
        ('BANK_TRANSFER', 'Bank Transfer'),    # Added for flexibility
    ]

    # Relationships
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    # Payment Details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # SIMPLIFIED: Removed currency field - always AFN for now
    # Can add back later when expanding internationally

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='CASH'
    )

    # Transaction Info
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        editable=False
    )
    external_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Transaction ID from payment gateway (M-Paisa, etc.)"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['booking']),
        ]

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} AFN ({self.status})"


class PaymentHistory(models.Model):
    """Track all payment status changes for audit trail"""

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='history'
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Payment histories'

    def __str__(self):
        return f"{self.payment.transaction_id}: {self.from_status} -> {self.to_status}"

