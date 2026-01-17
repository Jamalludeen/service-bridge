from django_filters.rest_framework import FilterSet
from .models import Booking


class MyBookingFilter(FilterSet):
    class Meta:
        model = Booking
        fields = {
            'status': ['exact']
        }