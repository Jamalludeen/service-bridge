import pytest
from booking.factories import BookingFactory
from booking.models import Booking


@pytest.mark.django_db
def test_create_booking():
    """Test create booking using factory"""

    booking = BookingFactory()

    assert booking.id is not None
    assert booking.customer is not None
    assert booking.professional is not None
    assert booking.service is not None
    assert booking.status == 'PENDING'

