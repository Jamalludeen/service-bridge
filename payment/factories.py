from factory.django import DjangoModelFactory
from decimal import Decimal
from faker import Faker
import factory
import uuid

from booking.factories import BookingFactory
from .models import Payment

fake = Faker()

class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment
    
    booking = factory.SubFactory(BookingFactory)
    amount = factory.LazyAttribute(lambda obj: Decimal(f"{fake.random_int(min=100, max=1000)}.{fake.random_int(min=0, max=99):02d}"))
    payment_method = 'CASH'
    status = 'PENDING'
    transaction_id = factory.LazyFunction(uuid.uuid4)