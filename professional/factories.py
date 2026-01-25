from factory.django import DjangoModelFactory
from .models import Professional
from core.factories import UserFactory
import factory
from faker import Faker

fake = Faker()

class ProfessionalFactory(DjangoModelFactory):
    class Meta:
        model = Professional
    
    # create a user with role 'professional'
    user = factory.SubFactory(UserFactory, role='professional')
    city = factory.LazyFunction(lambda: fake.city() )
    bio = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    years_of_experience = factory.LazyFunction(lambda: fake.random_int(min=0, max=10))
    verification_status = 'VERIFIED'
    services = factory.LazyFunction(lambda: [])  # You can customize this to add actual ServiceCategory instances if needed
    