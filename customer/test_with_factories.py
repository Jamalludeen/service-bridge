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

