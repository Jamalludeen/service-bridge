import pytest
from customer import factories

@pytest.mark.django_db
def test_create_customer_profile_with_factory():
    customer = factories.CustomerFactory()

    assert customer.id is not None
    assert customer.preferred_language is not None

