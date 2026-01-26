from factory.django import DjangoModelFactory
from datetime import date, time, timedelta
from decimal import Decimal
from faker import Faker
import factory

from professional.factories import ProfessionalFactory 
from customer.factories import CustomerFactory
from service.factories import ServiceFactory
from .models import Booking

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

