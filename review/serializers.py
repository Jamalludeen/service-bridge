
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

class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a review"""

    class Meta:
        model = Review
        fields = ['booking', 'rating', 'comment']

    def validate_booking(self, value):
        """Ensure booking is completed and belongs to the user"""
        request = self.context.get('request')
        user = request.user

        # Check if booking exists and belongs to user
        try:
            booking = Booking.objects.get(id=value.id, customer__user=user)
        except Booking.DoesNotExist:
            raise serializers.ValidationError(
                "Booking not found or doesn't belong to you."
            )

        # Check if booking is completed
        if booking.status != 'COMPLETED':
            raise serializers.ValidationError(
                "You can only review completed bookings."
            )

        # Check if review already exists
        if hasattr(booking, 'review'):
            raise serializers.ValidationError(
                "You have already reviewed this booking."
            )

        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        booking = validated_data['booking']

        # Automatically set customer and professional
        validated_data['customer'] = request.user
        validated_data['professional'] = booking.professional

        review = Review.objects.create(**validated_data)

        # Update professional's average rating
        self.update_professional_rating(booking.professional)

        return review
    
    def update_professional_rating(self, professional):
        """Recalculate and update professional's average rating"""
        avg_rating = Review.objects.filter(
            professional=professional,
            is_approved=True
        ).aggregate(avg=Avg('rating'))['avg']

        total_reviews = Review.objects.filter(
            professional=professional,
            is_approved=True
        ).count()

        professional.avg_rating = round(avg_rating, 2) if avg_rating else 0.0
        professional.total_reviews = total_reviews
        professional.save(update_fields=['avg_rating', 'total_reviews'])
    