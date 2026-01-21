from rest_framework.test import APIClient

import pytest
from decimal import Decimal
from datetime import date, time

from core.models import User
from customer.models import CustomerProfile
from professional.models import Professional
from booking.models import Booking
from payment.models import Payment



@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testcustomer',
        email='customer@gmail.com',
        password='TestPass123',
        phone='+93700000001',
        role='customer',
        is_verified=True
    )

@pytest.fixture
def professional_user(db):
    return User.objects.create_user(
        username='testprofessional',
        email='pro@gmail.com',
        password='testpAss123',
        phone='+93700000002',
        role='professional',
        is_verified=True
    )

@pytest.fixture
def admin_user(db):
    """Creates an admin user."""
    return User.objects.create_user(
        username='testadmin',
        email='admin@test.com',
        password='testpass123',
        phone='+93700000003',
        role='admin',
        is_staff=True,
        is_superuser=True,
        is_verified=True
    )

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return APIClient

@pytest.fixture
def professional_client(api_client, professional_user):
    api_client.force_authenticate(user=professional_user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def customer_profile(user, db):
    from customer.models import CustomerProfile
    return CustomerProfile.objects.create(
        user=user,
        city='kabul',
        district='13th'
    )

@pytest.fixture
def professional(professional_user, db):
    from professional.models import Professional, ServiceCategory

    category = ServiceCategory.objects.create(name='Plumbing')

    pro = Professional.objects.create(
        user=professional_user,
        years_of_experience=5,
        city='Kabul',
        bio='Professional plumber',
        verification_status='VERIFIED',
        is_active=True
    )
    pro.services.add(category)
    return pro

@pytest.fixture
def service(professional, db):
    from service.models import Service
    from professional.models import ServiceCategory

    category = ServiceCategory.objects.first()

    return Service.objects.create(
        professional=professional,
        category=category,
        title='Fix Broken pipe',
        pricing_type='FIXED',
        price_per_unit=Decimal('500.00'),
        is_active=True
    )

@pytest.fixture
def booking(customer_profile, professional, service, db):
    return Booking.objects.create(
        customer=customer_profile,
        professional=professional,
        service=service,
        scheduled_date=date(2026, 2, 1),
        scheduled_time=time(10, 0),
        address='123 Test Street',
        city='Kabul',
        quantity=1,
        estimated_price=Decimal('500.00'),
        status='PENDING'
    )