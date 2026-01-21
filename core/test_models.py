import pytest
from core.models import User

@pytest.mark.django_db
def test_user_creation():
    # ARRANGE: set up test data
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        phone='+93700000000',
        role='customer'
    )

    # ASSERT
    assert user.id is not None
    assert user.email == 'test@example.com'
    assert user.role == 'customer'
    assert user.check_password('testpass123')


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

