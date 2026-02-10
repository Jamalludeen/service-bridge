import pytest
from decimal import Decimal

from customer import factories
from customer.models import CustomerProfile


@pytest.mark.django_db
def test_create_customer_profile_with_factory():
    """Test that CustomerFactory creates a valid CustomerProfile instance."""
    customer = factories.CustomerFactory()

    assert customer.id is not None
    assert customer.pk is not None
    assert isinstance(customer, CustomerProfile)
    assert CustomerProfile.objects.filter(pk=customer.pk).exists()


@pytest.mark.django_db
def test_create_customer_batch():
    """Test creating multiple CustomerProfiles with factory batch."""
    customers = factories.CustomerFactory.create_batch(5)

    assert len(customers) == 5
    assert CustomerProfile.objects.count() == 5

    for customer in customers:
        assert customer.id is not None
        assert customer.user is not None


@pytest.mark.django_db
def test_customer_factory_default_values():
    """Test that CustomerFactory sets correct default values."""
    customer = factories.CustomerFactory()

    assert customer.preferred_language == 'fa'
    assert customer.total_bookings == 0
    assert customer.avg_rating_given == 0.0


@pytest.mark.django_db
def test_customer_factory_custom_overrides():
    """Test that CustomerFactory accepts custom field overrides."""
    customer = factories.CustomerFactory(
        city='Kabul',
        district='District 10',
        detailed_address='123 Main Street',
        preferred_language='en',
        total_bookings=15,
        avg_rating_given=4.5,
    )

    assert customer.city == 'Kabul'
    assert customer.district == 'District 10'
    assert customer.detailed_address == '123 Main Street'
    assert customer.preferred_language == 'en'
    assert customer.total_bookings == 15
    assert customer.avg_rating_given == 4.5


@pytest.mark.django_db
def test_customer_factory_linked_user_role():
    """Test that the linked user has role 'customer' and is verified."""
    customer = factories.CustomerFactory()

    assert customer.user is not None
    assert customer.user.role == 'customer'
    assert customer.user.is_verified is True
    assert customer.user.email.endswith('@gmail.com')

