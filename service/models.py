from django.db import models
from django.core.validators import FileExtensionValidator

from professional.models import Professional, ServiceCategory

from os.path import join

def service_image_upload_path(instance, filename):
    username: str = instance.professional.user.username.replace(" ", "_")
    username = username.replace(".", "_")
    return join("service_images", username, filename)


class Service(models.Model):
    PRICING_TYPE = (
        ('HOURLY', 'Hourly'),
        ('DAILY', 'Daily'),
        ('FIXED', 'Fixed'),
        ('PER_UNIT', 'Per Unit'),
    )

    professional = models.ForeignKey(
        Professional, on_delete=models.CASCADE, related_name="offered_services"
    )
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(
        null=True, blank=True, 
        upload_to=service_image_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPE)

    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['professional', 'category']),
        ]

    def __str__(self):
        return f'{self.professional.user.username} - {self.title}'
    
    @property
    def professional_location(self):
        """Return professional's location as (lat, lon) tuple"""
        if self.professional.latitude and self.professional.longitude:
            return (float(self.professional.latitude), float(self.professional.longitude))
        return None
    
    def distance_from(self, lat: float, lon: float):
        """Calculate distance from given coordinates"""
        from core.utils.location import haversine_distance

        prof_location = self.professional_location
        if prof_location:
            return haversine_distance(lat, lon, prof_location[0], prof_location[1])
        return None
