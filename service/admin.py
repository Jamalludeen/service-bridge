from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "professional", "category", "pricing_type", "price_per_unit"]
    