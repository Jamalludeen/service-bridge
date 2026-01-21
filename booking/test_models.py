import pytest
from decimal import Decimal
from datetime import date, time
from booking.models import Booking

@pytest.mark.django_db
def test_booking_creation(booking):
    assert booking.id is not None
    assert booking.status == 'PENDING'
    assert booking.customer is not None
    assert booking.professional is not None
    assert booking.service is not None
    assert booking.estimated_price == Decimal('500.00')


