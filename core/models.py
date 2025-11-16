from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("professional", "Professional"),
        ("admin", "Admin"),
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=20)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    faild_attempts = models.IntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
