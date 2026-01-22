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

@pytest.mark.django_db
def test_booking_string_representation(booking):
    """
    Test __str__() method of Booking.

    WHAT WE'RE TESTING:
    - str(booking) returns the expected format
    """
    expected = f"Booking #{booking.id} - {booking.service.title} (PENDING)"
    assert str(booking) == expected


@pytest.mark.django_db
def test_booking_status_changes(booking):
    """
    Test that booking status can be changed.
    """
    booking.status = 'ACCEPTED'
    booking.save()

    # Reload from database to verify it was saved
    booking.refresh_from_db()

    assert booking.status == 'ACCEPTED'


@pytest.mark.django_db
def test_booking_final_price_can_differ_from_estimated(booking):
    """
    Test that final_price can be different from estimated_price
    """

    assert booking.estimated_price == Decimal('500.00')
    assert booking.final_price is None

    booking.final_price = Decimal('650.00')
    booking.save()

    booking.refresh_from_db()
    assert booking.final_price == Decimal('650.00')
    assert booking.estimated_price == Decimal('500.00')  # Unchanged


@pytest.mark.django_db
def test_booking_quantity_validation(customer_profile, professional, service):
    """
    Test that quantity must be at least 1
    """

    from django.core.exceptions import ValidationError

    booking = Booking(
        customer=customer_profile,
        professional=professional,
        service=service,
        scheduled_date=date(2026, 2, 1),
        scheduled_time=time(10,0),
        address='street 123',
        city='Kabul',
        quantity='Kabul',
        estimated_price=Decimal('500.00')
    )

    with pytest.raises(ValidationError):
        booking.full_clean()

