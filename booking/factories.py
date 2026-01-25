import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal
from datetime import date, time, timedelta

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

    scheduled_date = factory.LazyFunction(lambda : fake.future_date(end_date=date.today() + timedelta(days=30)))
    # produce a real datetime.time object at an hour between 8 and 18
    scheduled_time = factory.LazyFunction(lambda: time(fake.random_int(8, 18), 0))

    address = factory.LazyFunction(lambda: fake.address())

    estimated_price = factory.LazyFunction(lambda: Decimal(fake.random_int(200, 2000)))

    status = 'PENDING'
    quantity = 1

