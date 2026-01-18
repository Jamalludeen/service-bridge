from django.core.validators import FileExtensionValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models

from os.path import join


User = get_user_model()


def professional_document_upload_path(instance, filename):
    username = getattr(instance.user, "username", "unknown_user").replace(" ", "_").replace(".", "_")
    return join("professional_documents", username, filename)


def professional_profile_upload_path(instance, filename):
    username = getattr(instance.user, "username", "unknown_user").replace(" ", "_").replace(".", "_")
    return join("professional_profiles", username, filename)



class ServiceCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Service Categories"
    
    

class Professional(models.Model):
    VERIFICATION_STATUS = (
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="professional_profile")
    
    city = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=0
    )

    services = models.ManyToManyField(ServiceCategory, related_name="professionals")
    
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='PENDING'
    )

    profile = models.FileField(
        upload_to=professional_profile_upload_path, blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])]
        )
    
    document = models.FileField(
            upload_to=professional_document_upload_path,blank=True, null=True,
            validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'pdf'])]
        )
    
    is_active = models.BooleanField(default=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Preferences 
    preferred_language = models.CharField(
        max_length=10, 
        choices=[("en","English"),("ps","Pashto"),("fa","Dari")], 
        default="fa"
    )

    # AI-based analytics
    avg_rating = models.FloatField(default=0.0)
    total_reviews = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.verification_status})"
    


