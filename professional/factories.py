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

    @factory.post_generation
    def services(self, create, extracted, **kwargs):
        """Attach service categories after creation.

        Usage in tests: ProfessionalFactory(services=[cat1, cat2])
        If not provided, a single ServiceCategoryFactory will be created and attached.
        """
        if not create:
            return

        if extracted:
            # extracted is expected to be an iterable of ServiceCategory instances
            for svc in extracted:
                self.services.add(svc)
        else:
            # lazy import to avoid circular imports at module import time
            from service.factories import ServiceCategoryFactory
            cat = ServiceCategoryFactory()
            self.services.add(cat)
    