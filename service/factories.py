import factory
from factory.django import DjangoModelFactory
from .models import Service, ServiceCategory
from professional.factories import ProfessionalFactory
from customer.factories import CustomerFactory
from faker import Faker
    
fake = Faker()


class ServiceCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ServiceCategory
    
    name = factory.LazyFunction(lambda: fake.word().title())

class ServiceFactory(DjangoModelFactory):
    class Meta:
        model = Service
    
    professional = factory.SubFactory(ProfessionalFactory)
    category = factory.SubFactory(ServiceCategoryFactory)
    title = factory.LazyFunction(lambda: fake.job())
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=1000))
    pricing_type = 'HOURLY'
    price_per_unit = factory.LazyFunction(lambda: fake.random_int(min=300, max=1200))
