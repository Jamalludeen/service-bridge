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


# ──────────────────────────────────────────────
# Cart View Tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
def test_cart_list_unauthenticated(api_client):
    """Unauthenticated users should get 401 on cart endpoint."""
    url = reverse('cart-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_cart_list_success(authenticated_client, customer_profile):
    """Authenticated customer gets their cart (auto-created if absent)."""
    url = reverse('cart-list')
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_empty'] is True
    assert response.data['total_items'] == 0


@pytest.mark.django_db
def test_cart_add_item(authenticated_client, customer_profile, service):
    """Customer can add a service to their cart."""
    url = reverse('cart-add')
    data = {'service': service.id, 'quantity': 2}
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == 'Item added to cart successfully'
    assert response.data['item']['quantity'] == 2


@pytest.mark.django_db
def test_cart_add_duplicate_item_increments_quantity(authenticated_client, customer_profile, service):
    """Adding the same service again should increment quantity, not duplicate."""
    url = reverse('cart-add')
    data = {'service': service.id, 'quantity': 1}

    # First add
    authenticated_client.post(url, data, format='json')

    # Second add
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Cart item quantity updated'
    assert response.data['item']['quantity'] == 2


@pytest.mark.django_db
def test_cart_add_item_invalid_service(authenticated_client, customer_profile):
    """Adding a non-existent service should fail with 400."""
    url = reverse('cart-add')
    data = {'service': 99999, 'quantity': 1}
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_cart_update_item_quantity(authenticated_client, customer_profile, service):
    """Customer can update a cart item's quantity."""
    # Create cart and item
    cart = Cart.objects.create(customer=customer_profile)
    item = CartItem.objects.create(cart=cart, service=service, quantity=1)

    url = reverse('cart-update-item', kwargs={'pk': cart.pk, 'item_id': item.pk})
    data = {'quantity': 5}
    response = authenticated_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Cart item updated successfully'

    item.refresh_from_db()
    assert item.quantity == 5


@pytest.mark.django_db
def test_cart_update_item_invalid_quantity(authenticated_client, customer_profile, service):
    """Updating a cart item with quantity 0 should fail."""
    cart = Cart.objects.create(customer=customer_profile)
    item = CartItem.objects.create(cart=cart, service=service, quantity=1)

    url = reverse('cart-update-item', kwargs={'pk': cart.pk, 'item_id': item.pk})
    data = {'quantity': 0}
    response = authenticated_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
