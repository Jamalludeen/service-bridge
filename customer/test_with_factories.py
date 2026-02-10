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


@pytest.mark.django_db
def test_customer_factory_str_representation():
    """Test CustomerProfile __str__ returns username."""
    customer = factories.CustomerFactory()

    assert str(customer) == customer.user.username


@pytest.mark.django_db
def test_customer_factory_location_fields():
    """Test that factory populates latitude and longitude with valid decimals."""
    customer = factories.CustomerFactory()

    assert customer.latitude is not None
    assert customer.longitude is not None
    assert isinstance(customer.latitude, Decimal)
    assert isinstance(customer.longitude, Decimal)
    assert -90 <= customer.latitude <= 90
    assert -180 <= customer.longitude <= 180


@pytest.mark.django_db
def test_customer_factory_preferred_language_choices():
    """Test that preferred_language can be set to each valid choice."""
    for lang_code in ['en', 'ps', 'fa']:
        customer = factories.CustomerFactory(preferred_language=lang_code)
        assert customer.preferred_language == lang_code


# ──────────────────────────────────────────────
# Cart Factory Tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
def test_create_cart_with_factory():
    """Test that CartFactory creates a valid Cart instance."""
    from customer.models import Cart

    cart = factories.CartFactory()

    assert cart.id is not None
    assert cart.pk is not None
    assert isinstance(cart, Cart)
    assert Cart.objects.filter(pk=cart.pk).exists()


@pytest.mark.django_db
def test_cart_factory_customer_relationship():
    """Test that CartFactory creates a linked CustomerProfile."""
    cart = factories.CartFactory()

    assert cart.customer is not None
    assert isinstance(cart.customer, CustomerProfile)
    assert cart.customer.user.role == 'customer'

