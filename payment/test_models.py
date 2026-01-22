import pytest
from decimal import Decimal
from .models import Payment, PaymentHistory


@pytest.mark.django_db
def test_payment_creation(payment):
    assert payment.id is not None
    assert payment.booking is not None
    assert payment.amount is not None
    assert payment.payment_method is not None
    assert payment.transaction_id is not None

