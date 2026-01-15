from django_filters.rest_framework import FilterSet

from .models import Service


class ServiceFilter(FilterSet):
    class Meta:
        model = Service
        fields = {
            'category': ['exact'],
            'pricing_type': ['exact'],
            'price_per_unit': ['lt', 'gt']
        }