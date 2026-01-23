import pytest
from decimal import Decimal
import uuid
from datetime import date, time

from .models import Payment, PaymentHistory
from booking.models import Booking

@pytest.mark.django_db
def test_payment_creation(payment):
    assert payment.id is not None
    assert payment.booking is not None
    assert payment.amount is not None
    assert payment.payment_method is not None
    assert payment.transaction_id is not None

@pytest.mark.django_db
def test_payment_transaction_id_is_unique(booking, customer_profile, professional, service):
    payment1 = Payment.objects.create(
        booking=booking,
        amount=Decimal('499.99'),
        transaction_id=f'{uuid.uuid4().hex[:12].upper()}',
    )

    booking2 = Booking.objects.create(
        customer=customer_profile,
        professional=professional,
        service=service,
        scheduled_date=date(2026, 3, 1),
        scheduled_time=time(14, 0),
        address='Another address',
        city='Kabul',
        estimated_price=Decimal('600.00')
    )

    payment2 = Payment.objects.create(
        booking=booking2,
        amount=Decimal('499.99'),
        transaction_id=f'{uuid.uuid4().hex[:12].upper()}',
    )

    assert payment1.transaction_id != payment2.transaction_id


@pytest.mark.django_db
def test_payment_amount_must_be_positive(booking):
    from django.core.exceptions import ValidationError
    payment = Payment.objects.create(
        booking=booking,
        amount=Decimal('-100.00'),
    )
    with pytest.raises(ValidationError):
        payment.full_clean()


@pytest.mark.django_db
def test_payment_str_representation(payment):
    expected = f"Payment {payment.transaction_id} - {payment.amount} AFN ({payment.status})"
    assert str(payment) == expected

