from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

from core.models import User
from booking.models import Booking


class Payment(models.Model):
    """payment model linked to a booking"""

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
    ]

    CURRENCY_CHOICES = [
        ('AFN', 'Afghan Afghani'),
        ('USD', 'US Dollar'),
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
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='AFN'
    )
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
        null=True,
        help_text="Transaction ID from payment gateway"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # Escrow Info
    escrow_held_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    # Platform Fee (optional - for future monetization)
    platform_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Platform commission percentage"
    )
    platform_fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    professional_payout = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount to be paid to professional after fees"
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

        # Calculate platform fee and professional payout
        if self.amount and not self.professional_payout:
            self.platform_fee_amount = (
                self.amount * self.platform_fee_percentage / 100
            )
            self.professional_payout = self.amount - self.platform_fee_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} {self.currency} ({self.status})"



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