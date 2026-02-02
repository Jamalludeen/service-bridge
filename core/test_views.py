from django.utils import timezone
from rest_framework import status
from django.urls import reverse
import pytest

from core.models import User



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

@pytest.mark.django_db
def test_verify_otp(api_client):
    # first register user
    user = User.objects.create_user(
        username='testcustomer',
        email='customer@gmail.com',
        password='TestPass123',
        phone='+93700000001',
        role='customer',
        is_verified=True,
        otp='123456',
        otp_created_at=timezone.now()
    )

    url = reverse('verify_otp')
    data = {
        'email': user.email,
        'otp': user.otp
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_verify_otp_with_invalid_otp(api_client):
    # first register user
    user = User.objects.create_user(
        username='testcustomer',
        email='customer@gmail.com',
        password='TestPass123',
        phone='+93700000001',
        role='customer',
        is_verified=True,
        otp='123456',
        otp_created_at=timezone.now()
    )

    url = reverse('verify_otp')
    data = {
        'email': user.email,
        'otp': f'{user.otp}0' # an extra 0 is concatenated with the original OTP to enforce its wrong case test
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_request_new_otp(api_client):
    user = User.objects.create_user(
        username='testcustomer',
        email='customer@gmail.com',
        password='TestPass123',
        phone='+93700000001',
        role='customer',
        is_verified=True,
        otp='123456',
        otp_created_at=timezone.now()
    )

    url = reverse('new_otp')
    data = {
        'email': user.email,
    }

    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_202_ACCEPTED

@pytest.mark.django_db
def test_request_new_otp_with_invalid_email(api_client):
    user = User.objects.create_user(
        username='testcustomer',
        email='customer@gmail.com',
        password='TestPass123',
        phone='+93700000001',
        role='customer',
        is_verified=True,
        otp='123456',
        otp_created_at=timezone.now()
    )

    url = reverse('new_otp')
    data = {
        'email': 'user@gmail.com',
    }

    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND
