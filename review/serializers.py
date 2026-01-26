
from rest_framework import serializers
from django.db.models import Avg

from .models import Review, ReviewResponse
from booking.models import Booking
from professional.models import Professional


class ReviewResponseSerializer(serializers.ModelSerializer):
    professional_name = serializers.CharField(
        source='professional.user.get_full_name',
        read_only=True
    )

    class Meta:
        model = ReviewResponse
        fields = [
            'id',
            'professional',
            'professional_name',
            'response_text',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['professional', 'created_at', 'updated_at']


class ReviewListSerializer(serializers.ModelSerializer):
    """Serializer for listing reviews"""

    customer_name = serializers.SerializerMethodField()
    service_title = serializers.CharField(
        source='booking.service.title',
        read_only=True
    )
    response = ReviewResponseSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'booking',
            'customer_name',
            'service_title',
            'rating',
            'comment',
            'response',
            'created_at',
            'updated_at'
        ]

    def get_customer_name(self, obj):
        """Return customer first name + last initial if available, else username"""
        user = obj.customer
        full_name = user.get_full_name()

        if full_name:
            return full_name
        return user.username
