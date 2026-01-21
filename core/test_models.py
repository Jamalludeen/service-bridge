import pytest
from core.models import User

@pytest.mark.django_db
def test_user_creation(user):
    # ARRANGE: set up test data
    assert user.id is not None
    assert user.email == 'customer@gmail.com'
    assert user.role == 'customer'


@pytest.mark.django_db
def test_user_role(user):
    assert user.role == 'customer'


@pytest.mark.django_db
def test_user_email_must_be_unique():
    from django.db import IntegrityError

    User.objects.create_user(
        username='user1',
        email='same@example.com',
        password='pass123',
        phone='+93700000001',
        role='customer'
    )

    with pytest.raises(IntegrityError):
        User.objects.create_user(
            username='user2',
            email='same@example.com',  # Same email!
            password='pass123',
            phone='+93700000002',
            role='customer'
        )


@pytest.mark.django_db
def test_user_string_representation():
    user = User.objects.create_user(
        username='johndoe',
        email='john@example.com',
        password='pass123',
        phone='+93700000003',
        role='customer'
    )

    assert str(user) == 'johndoe'

