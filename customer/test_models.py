import pytest
from django.contrib.auth import get_user_model
from service.models import Service  # Assuming Service model exists in service app
from .models import CustomerProfile, Cart, CartItem

User = get_user_model()

@pytest.mark.django_db
def test_customer_profile_creation():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
    profile = CustomerProfile.objects.create(user=user, phone='+1234567890', address='123 Test St')
    
    assert profile.user == user
    assert profile.phone == '+1234567890'
    assert profile.address == '123 Test St'

@pytest.mark.django_db
def test_customer_profile_str():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
    profile = CustomerProfile.objects.create(user=user)
    
    assert str(profile) == f'Customer Profile for {user.username}'

@pytest.mark.django_db
def test_cart_creation():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
    profile = CustomerProfile.objects.create(user=user)
    cart = Cart.objects.create(customer=profile)
    
    assert cart.customer == profile
    assert cart.total_items == 0

@pytest.mark.django_db
def test_cart_total_items():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
    profile = CustomerProfile.objects.create(user=user)
    cart = Cart.objects.create(customer=profile)
    service = Service.objects.create(title='Test Service', price=100)
    
    CartItem.objects.create(cart=cart, service=service, quantity=2)
    CartItem.objects.create(cart=cart, service=service, quantity=3)
    
    assert cart.total_items == 5

@pytest.mark.django_db
def test_cart_item_creation():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
    profile = CustomerProfile.objects.create(user=user)
    cart = Cart.objects.create(customer=profile)
    service = Service.objects.create(title='Test Service', price=100)
    item = CartItem.objects.create(cart=cart, service=service, quantity=1)
    
    assert item.cart == cart
    assert item.service == service
    assert item.quantity == 1

@pytest.mark.django_db
def test_cart_item_quantity_update():
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
    profile = CustomerProfile.objects.create(user=user)
    cart = Cart.objects.create(customer=profile)
    service = Service.objects.create(title='Test Service', price=100)
    item = CartItem.objects.create(cart=cart, service=service, quantity=1)
    
    item.quantity = 5
    item.save()
    item.refresh_from_db()
    
    assert item.quantity == 5