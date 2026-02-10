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

