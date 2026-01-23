import pytest
from rest_framework import status
from django.urls import reverse



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
def test_create_booking_as_customer(authenticated_client, service, customer_profile, professional):
    url = reverse('booking-list')
    data = {
        'service_id': service.id,
        'scheduled_date': '2026-02-01',
        'scheduled_time': '10:00:00',
        'address': '123 Main St',
        'city': 'Metropolis',
        'estimated_price': '150.00',
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED