from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from django.db.models import Q

from .models import Service


class ServiceFilter(FilterSet):
    # Existing filters
    category = NumberFilter(field_name='category', lookup_expr='exact')
    pricing_type = CharFilter(field_name='pricing_type', lookup_expr='exact')
    price_per_unit__lt = NumberFilter(field_name='price_per_unit', lookup_expr='lt')
    price_per_unit__gt = NumberFilter(field_name='price_per_unit', lookup_expr='gt')

    # Location filters
    city = CharFilter(field_name='professional__city', lookup_expr='icontains')
    min_rating = NumberFilter(field_name='professional__avg_rating', lookup_expr='gte')

    class Meta:
        model = Service
        fields = {
            'category': ['exact'],
            'pricing_type': ['exact'],
            'price_per_unit': ['lt', 'gt']
        }