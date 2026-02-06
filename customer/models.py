from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from uuid import uuid4

from os.path import join

from service.models import Service

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

    def __str__(self):
        return str(self.user.username)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "customer_cart"
        verbose_name = "Shopping Cart"
        verbose_name_plural = "Shopping Carts"
        indexes = [
            models.Index(fields=['customer'])
        ]

    def __str__(self):
        return f'Cart {self.id}'
    
    @property
    def total_item(self):
        return self.items.count()
    
    @property
    def total_price(self):
        from decimal import Decimal
        total = Decimal("0.0")
        for item in self.items.selected_related("service"):
            total += item.estimated_price
        return total
    
    def clear(self):
        self.items.all().delete()
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='cart_items')
