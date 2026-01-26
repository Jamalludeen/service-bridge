
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
