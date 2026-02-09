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
