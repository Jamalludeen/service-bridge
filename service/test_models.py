import pytest
from decimal import Decimal
from time import sleep

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import User
from professional.models import Professional, ServiceCategory
from service.models import Service, service_image_upload_path


@pytest.mark.django_db
def test_service_creation_defaults(professional):
    category = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Plumbing")

    service = Service.objects.create(
        professional=professional,
        category=category,
        title="Fix broken pipe",
        description="Repair broken pipe and leaks",
        pricing_type="FIXED",
        price_per_unit=Decimal("500.00"),
    )

    assert service.id is not None
    assert service.is_active is True
    assert service.created_at is not None


@pytest.mark.django_db
def test_service_string_representation(professional):
    category = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Plumbing")

    service = Service.objects.create(
        professional=professional,
        category=category,
        title="AC repair",
        description="Repair AC",
        pricing_type="HOURLY",
        price_per_unit=Decimal("100.00"),
    )

    assert str(service) == f"{professional.user.username} - {service.title}"


@pytest.mark.django_db
def test_service_ordering_newest_first(professional):
    category = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Plumbing")

    older = Service.objects.create(
        professional=professional,
        category=category,
        title="Older service",
        description="Older",
        pricing_type="FIXED",
        price_per_unit=Decimal("10.00"),
    )

    sleep(0.2)

    newer = Service.objects.create(
        professional=professional,
        category=category,
        title="Newer service",
        description="Newer",
        pricing_type="FIXED",
        price_per_unit=Decimal("20.00"),
    )

    services = list(Service.objects.all())
    assert services[0].id == newer.id
    assert services[1].id == older.id


@pytest.mark.django_db
def test_service_image_upload_path_sanitizes_username(professional_user):
    user = User.objects.create_user(
        username="john doe.test",
        email="john@example.com",
        password="TestPass123",
        phone="+93700000999",
        role="professional",
        is_verified=True,
    )

    category = ServiceCategory.objects.create(name="Electrical")

    pro = Professional.objects.create(
        user=user,
        years_of_experience=3,
        city="Kabul",
        bio="Electrician",
        verification_status="VERIFIED",
        is_active=True,
    )
    pro.services.add(category)

    instance = Service(
        professional=pro,
        category=category,
        title="Wiring",
        description="House wiring",
        pricing_type="FIXED",
        price_per_unit=Decimal("100.00"),
    )

    path = service_image_upload_path(instance, "photo.png")
    assert path.startswith("service_images/john_doe_test/")
    assert path.endswith("/photo.png")


@pytest.mark.django_db
def test_service_image_extension_validation(professional):
    category = ServiceCategory.objects.first() or ServiceCategory.objects.create(name="Plumbing")

    invalid_file = SimpleUploadedFile(
        "image.gif",
        b"fake-content",
        content_type="image/gif",
    )

    service = Service(
        professional=professional,
        category=category,
        title="Bad image",
        description="Should fail validation",
        pricing_type="FIXED",
        price_per_unit=Decimal("10.00"),
        image=invalid_file,
    )

    with pytest.raises(ValidationError):
        service.full_clean()


@pytest.mark.django_db
def test_service_professional_location_none_when_missing_coords(service, professional):
    professional.latitude = None
    professional.longitude = None
    professional.save(update_fields=["latitude", "longitude"])

    service.refresh_from_db()
    assert service.professional_location is None
    assert service.distance_from(34.5, 69.1) is None


@pytest.mark.django_db
def test_service_distance_from_returns_value_when_coords_present(service, professional):
    professional.latitude = 34.5281
    professional.longitude = 69.1714
    professional.save(update_fields=["latitude", "longitude"])

    service.refresh_from_db()

    distance = service.distance_from(34.5281, 69.1714)
    assert distance is not None
    assert distance == pytest.approx(0.0, abs=1e-6)
