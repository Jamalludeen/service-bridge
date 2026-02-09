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
