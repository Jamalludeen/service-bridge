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
