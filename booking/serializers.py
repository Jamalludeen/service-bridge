from rest_framework import serializers

from django.utils import timezone

from .models import Booking, BookingStatusHistory
from service.serializers import CustomerServiceSerializer
from professional.serializers import ProfessionalSerializer
from customer.serializers import CustomerRetrieveProfileSerializer



class BookingCreateSerializer(serializers.ModelSerializer):
    """For customers creating bookings"""
    service_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = [
            'service_id', 'scheduled_date', 'scheduled_time',
            'address', 'city', 'latitude', 'longitude',
            'special_instructions', 'quantity'
        ]

    def validate_service_id(self, value):
        from service.models import Service
        try:
            service = Service.objects.select_related('professional').get(
                id=value, is_active=True
            )
            if service.professional.verification_status != 'VERIFIED':
                raise serializers.ValidationError(
                    "This professional is not verified yet."
                )
            if not service.professional.is_active:
                raise serializers.ValidationError(
                    "This professional is currently unavailable."
                )
        except Service.DoesNotExist:
            raise serializers.ValidationError("Service not found or inactive.")
        return value

    def validate_scheduled_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Scheduled date cannot be in the past."
            )
        return value

    def validate(self, attrs):
        # Calculate estimated price
        from service.models import Service
        service = Service.objects.get(id=attrs['service_id'])
        quantity = attrs.get('quantity', 1)

        if service.pricing_type == 'FIXED':
            attrs['estimated_price'] = service.price_per_unit
        else:
            attrs['estimated_price'] = service.price_per_unit * quantity

        return attrs

    def create(self, validated_data):
        from service.models import Service
        service_id = validated_data.pop('service_id')
        service = Service.objects.get(id=service_id)

        customer = self.context['request'].user.customerprofile

        booking = Booking.objects.create(
            customer=customer,
            professional=service.professional,
            service=service,
            **validated_data
        )

        # Create initial status history
        BookingStatusHistory.objects.create(
            booking=booking,
            to_status='PENDING',
            changed_by=self.context['request'].user,
            note='Booking created'
        )

        return booking
