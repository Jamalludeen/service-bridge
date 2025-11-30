from django.contrib import admin
from .models import CustomerProfile

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'city', 'profile_image']


