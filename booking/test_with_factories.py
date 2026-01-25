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

@pytest.mark.django_db
def test_create_multiple_bookings():
    """Test creating multiple bookings using factory"""

    bookings = BookingFactory.create_batch(5)

    assert len(bookings) == 5
    assert Booking.objects.count() == 5

    for booking in bookings:
        assert booking.id is not None
        assert booking.customer is not None
        assert booking.professional is not None
        assert booking.service is not None
        assert booking.status == 'PENDING'

@pytest.mark.django_db
def test_create_bookings_for_same_customer():
    """Test creating multiple bookings for the same customer"""

    from customer.factories import CustomerFactory
    customer = CustomerFactory()
    bookings = BookingFactory.create_batch(3, customer=customer)
    
    assert all(booking.customer == customer for booking in bookings)
    assert customer.bookings.count() == 3