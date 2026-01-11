from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "professional", "category", "title", "description", "pricing_type", "price_per_unit", "is_active"]

