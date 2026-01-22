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


@pytest.mark.django_db
def test_booking_relationships(booking):
    """
    Test that booking relationships work in both directions.
    """
    
    assert booking.customer.user.email == 'customer@gmail.com'
    customer_bookings = booking.customer.bookings.all()
    assert booking in customer_bookings

    pro_bookings = booking.professional.booking_requests.all()
    assert booking in pro_bookings


@pytest.mark.django_db
def test_booking_ordering(customer_profile, professional, service, booking):
    """
    Test that bookings are ordered by created_at (newest first)
    """
    from time import sleep

    booking1 = Booking.objects.create(
        customer=customer_profile,
        professional=professional,
        service=service,
        scheduled_date=date(2026, 2,2),
        scheduled_time=time(10, 0),
        address="city #1 home #1",
        city="city 1",
        estimated_price=Decimal('500.00'),
    )

    sleep(0.5)

    booking2 = Booking.objects.create(
        customer=customer_profile,
        professional=professional,
        service=service,
        scheduled_date=date(2026, 2,2),
        scheduled_time=time(11, 0),
        address="city #2 home #2",
        city="city 2",
        estimated_price=Decimal('500.00'),
    )

    booking.refresh_from_db()
    bookings = list(Booking.objects.all())
    # print("bookings----------: ", bookings)

    assert bookings[0].id == booking2.id
    assert bookings[1].id == booking1.id


    
