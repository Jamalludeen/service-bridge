from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator


from os.path import join

User = get_user_model()


def profile_picture_upload_path(instance, filename):
    username: str = instance.user.username.replace(" ", "_")
    username = username.replace(".", "_")
    return join("customer_profiles", username, filename)


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(
        upload_to=profile_picture_upload_path, null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])]
        )

    # Address, Map, Location 
    city = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    detailed_address = models.TextField(null=True, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Preferences 
    preferred_language = models.CharField(
        max_length=10, 
        choices=[("en","English"),("ps","Pashto"),("fa","Dari")], 
        default="fa"
    )

    # AI-based analytics
    total_bookings = models.IntegerField(default=0)
    avg_rating_given = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

