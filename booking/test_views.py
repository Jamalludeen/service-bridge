import pytest
from rest_framework import status
from django.urls import reverse
from .models import Booking


@pytest.mark.django_db
def test_bookings_unauthenticated(api_client):
    urls = reverse('booking-list')
    response = api_client.get(urls)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_bookings_list_with_authenticated_user(authenticated_client):
    urls = reverse('booking-list')
    response = authenticated_client.get(urls)

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_booking_retrieve_with_unauthenticated_user(api_client, booking):
    urls = reverse('booking-detail', args=[booking.id])
    response = api_client.get(urls)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_booking_retrieve_with_authenticated_user(authenticated_client, booking):
    url = reverse('booking-detail', args=[booking.id])
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    assert response.data.get('id') == booking.id

@pytest.mark.django_db
def test_create_booking_as_customer(authenticated_client, service):
    url = reverse('booking-list')
    data = {
        'service_id': service.id,
        'scheduled_date': '2026-02-01',
        'scheduled_time': '10:00:00',
        'address': '123 Main St',
        'city': 'Metropolis',
        'estimated_price': '150.00',
        'quantity': 7,
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    assert 'id' in response.data
    assert response.data['status'] == 'PENDING'

    booking_id = response.data['id']
    assert Booking.objects.filter(id=booking_id).exists()

    booking = Booking.objects.get(id=booking_id)
    assert booking.city == 'Metropolis'
    assert booking.quantity == 7

@pytest.mark.django_db
def test_create_booking_with_invalid_data(authenticated_client):
    url = reverse('booking-list')
    data = {
        'service_id': 9999,  # assuming this service does not exist
        'scheduled_date': 'invalid-date',
        'scheduled_time': '10:00:00',
        'address': '',
        'city': 'Metropolis',
        'estimated_price': '-50.00',
        'quantity': 0,
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    