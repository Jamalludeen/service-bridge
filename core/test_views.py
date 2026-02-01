import pytest
from django.urls import reverse
from rest_framework import status



@pytest.mark.django_db
def test_login_with_valid_password(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': 'TestPass123'
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    
@pytest.mark.django_db
def test_login_with_invalid_password(api_client, user):
    url = reverse('login')
    data = {
        'email': user.email,
        'password': '1234'
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
