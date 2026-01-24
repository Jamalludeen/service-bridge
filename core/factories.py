import factory
from factory.django import DjangoModelFactory
from faker import Faker

from .models import User 



class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@gmail.com')
    phone = factory.Sequence(lambda n: f'+9370000{n:04d}')

    # default role
    role = 'customer'

    # default verified
    is_verified = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password for the user."""
        if create:
            password = extracted or 'testPass123'
            obj.set_password(password)
            obj.save()

