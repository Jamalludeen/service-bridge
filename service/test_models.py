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

