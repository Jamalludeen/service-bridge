from django.db import models
from professional.models import Professional, ServiceCategory


class Service(models.Model):
    PRICING_TYPE = (
        ('HOURLY', 'Hourly'),
        ('DAILY', 'Daily'),
        ('FIXED', 'Fixed'),
        ('PER_UNIT', 'Per Unit'),
    )

    professional = models.ForeignKey(
        Professional, on_delete=models.CASCADE, related_name="services"
    )
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPE)

    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    