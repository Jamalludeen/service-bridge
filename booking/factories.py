import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal
from datetime import date, time

from .models import Booking
from core.factories import UserFactory
from customer.factories import CustomerFactory
from professional.factories import ProfessionalFactory 
from service.factories import ServiceFactory

fake = Faker()


class BookingFactory(DjangoModelFactory):
    class Meta:
        model = Booking
    
    customer = factory.SubFactory(CustomerFactory)
    professional = factory.SubFactory(ProfessionalFactory)
    service = factory.SubFactory(ServiceFactory)

    scheduled_date = factory.LazyAttribute(lambda _: fake.future_date(end_date='+30d'))
    scheduled_time = factory.LazyAttribute(lambda _: fake.time(fake.random_int(8, 18), 0))

    address = factory.LazyAttribute(lambda _: fake.address())

    estimated_price = factory.LazyAttribute(lambda _: Decimal(fake.random_int(200, 2000)))

    status = 'PENDING'
    quantity = 1
    
