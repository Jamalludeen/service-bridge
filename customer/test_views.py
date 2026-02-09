import pytest
from rest_framework import status
from django.urls import reverse
from customer.models import CustomerProfile, Cart, CartItem


# ──────────────────────────────────────────────
# Customer Profile View Tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
def test_profile_get_unauthenticated(api_client):
    """Unauthenticated users should get 401 on profile endpoint."""
    url = reverse('profile')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_profile_get_success(authenticated_client, customer_profile):
    """Authenticated customer should retrieve their profile."""
    url = reverse('profile')
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['city'] == customer_profile.city
    assert response.data['district'] == customer_profile.district


@pytest.mark.django_db
def test_profile_patch_update_city_and_district(authenticated_client, customer_profile):
    """Customer can update their city and district."""
    url = reverse('profile')
    data = {'city': 'Herat', 'district': '5th'}
    response = authenticated_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['data']['city'] == 'Herat'
    assert response.data['data']['district'] == '5th'

    customer_profile.refresh_from_db()
    assert customer_profile.city == 'Herat'
    assert customer_profile.district == '5th'


@pytest.mark.django_db
def test_profile_patch_update_nested_user_data(authenticated_client, customer_profile):
    """Customer can update nested user fields (first_name, phone, email)."""
    url = reverse('profile')
    data = {
        'user': {
            'first_name': 'Ahmad',
            'last_name': 'Karimi',
            'email': 'ahmad.karimi@gmail.com',
            'phone': '+93700000099',
        }
    }
    response = authenticated_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK

    customer_profile.user.refresh_from_db()
    assert customer_profile.user.first_name == 'Ahmad'
    assert customer_profile.user.last_name == 'Karimi'
    assert customer_profile.user.email == 'ahmad.karimi@gmail.com'
    assert customer_profile.user.phone == '+93700000099'


@pytest.mark.django_db
def test_profile_patch_invalid_email(authenticated_client, customer_profile):
    """Non-Gmail email should be rejected."""
    url = reverse('profile')
    data = {'user': {'email': 'bad@yahoo.com'}}
    response = authenticated_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_profile_patch_invalid_phone(authenticated_client, customer_profile):
    """Non-Afghan phone number should be rejected."""
    url = reverse('profile')
    data = {'user': {'phone': '+1234567890'}}
    response = authenticated_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'phone' in response.data


@pytest.mark.django_db
def test_profile_delete_success(authenticated_client, customer_profile):
    """Customer can delete their own profile."""
    url = reverse('profile')
    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not CustomerProfile.objects.filter(id=customer_profile.id).exists()
