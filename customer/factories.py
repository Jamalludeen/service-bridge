import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal

from .models import CustomerProfile, Cart, CartItem
from core.factories import UserFactory
from service.factories import ServiceFactory


fake = Faker()


class CustomerFactory(DjangoModelFactory):
    """Factory for creating CustomerProfile with a linked User."""

    class Meta:
        model = CustomerProfile

    # create a user with role 'customer'
    user = factory.SubFactory(UserFactory, role='customer')

    city = factory.LazyFunction(lambda: fake.city())
    district = factory.LazyFunction(lambda: fake.word())
    detailed_address = factory.LazyFunction(lambda: fake.address())

    latitude = factory.LazyFunction(lambda: Decimal(str(fake.latitude())))
    longitude = factory.LazyFunction(lambda: Decimal(str(fake.longitude())))

    preferred_language = 'fa'
    total_bookings = 0
    avg_rating_given = 0.0


class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart
    customer = factory.SubFactory(CustomerFactory)

class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem
    
    cart = factory.SubFactory(CartFactory)
    service = factory.SubFactory(ServiceFactory)
    
    
