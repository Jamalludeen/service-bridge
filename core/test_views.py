from rest_framework import status
from django.urls import reverse
import pytest



@pytest.mark.django_db
def test_login_with_valid_credentials(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'TestPass123'
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_login_with_invalid_credentials(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': '1234'
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_customer_registration_view(api_client):
    url = reverse('customer_register')
    data = {
        'username': 'John.Smith',
        'email': 'john.smith@gmail.com',
        'phone': '+93788727887',
        'password': 'ILoveDjango',
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
