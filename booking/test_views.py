import pytest
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from booking.models import Booking



@pytest.mark.django_db
def test_bookings_unauthenticated(api_client):
    urls = reverse('booking-list')
    response = api_client.get(urls)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

