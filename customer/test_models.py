import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from service.models import Service
from .models import CustomerProfile, Cart, CartItem

User = get_user_model()

@pytest.mark.django_db
def test_customer_profile_creation():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
    profile = CustomerProfile.objects.create(
        user=user,
        city='Kabul',
        district='13th',
        detailed_address='123 Test St'
    )

    assert profile.user == user
    assert profile.city == 'Kabul'
    assert profile.district == '13th'
    assert profile.detailed_address == '123 Test St'

@pytest.mark.django_db
def test_customer_profile_str():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
    profile = CustomerProfile.objects.create(user=user)

    assert str(profile) == user.username

@pytest.mark.django_db
def test_cart_creation(customer_profile):
    cart = Cart.objects.create(customer=customer_profile)

    assert cart.customer == customer_profile
    assert cart.total_items == 0

@pytest.mark.django_db
def test_cart_total_items(customer_profile, service):
    cart = Cart.objects.create(customer=customer_profile)

    CartItem.objects.create(cart=cart, service=service, quantity=2)
    second_service = Service.objects.create(
        professional=service.professional,
        category=service.category,
        title='Second Service',
        description='Another test service',
        pricing_type='FIXED',
        price_per_unit=Decimal('200.00'),
        is_active=True
    )
    CartItem.objects.create(cart=cart, service=second_service, quantity=3)

    assert cart.total_items == 2

@pytest.mark.django_db
def test_cart_item_creation(customer_profile, service):
    cart = Cart.objects.create(customer=customer_profile)
    item = CartItem.objects.create(cart=cart, service=service, quantity=1)

    assert item.cart == cart
    assert item.service == service
    assert item.quantity == 1

@pytest.mark.django_db
def test_cart_item_quantity_update(customer_profile, service):
    cart = Cart.objects.create(customer=customer_profile)
    item = CartItem.objects.create(cart=cart, service=service, quantity=1)

    item.quantity = 5
    item.save()
    item.refresh_from_db()

    assert item.quantity == 5