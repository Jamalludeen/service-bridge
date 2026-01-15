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



class BookingListSerializer(serializers.ModelSerializer):
    """For listing bookings"""
    service_title = serializers.CharField(source='service.title', read_only=True)
    professional_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'service_title', 'professional_name', 'customer_name',
            'scheduled_date', 'scheduled_time', 'status',
            'estimated_price', 'final_price', 'city', 'created_at'
        ]

    def get_professional_name(self, obj):
        return obj.professional.user.get_full_name() or obj.professional.user.username

    def get_customer_name(self, obj):
        return obj.customer.user.get_full_name() or obj.customer.user.username



class BookingDetailSerializer(serializers.ModelSerializer):
    """For detailed booking view"""
    service = CustomerServiceSerializer(read_only=True)
    professional = ProfessionalSerializer(read_only=True)
    customer = CustomerRetrieveProfileSerializer(read_only=True)
    status_history = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'professional', 'service',
            'scheduled_date', 'scheduled_time',
            'address', 'city', 'latitude', 'longitude',
            'special_instructions', 'quantity',
            'estimated_price', 'final_price',
            'status', 'rejection_reason', 'cancellation_reason',
            'created_at', 'accepted_at', 'started_at', 'completed_at',
            'status_history'
        ]

    def get_status_history(self, obj):
        history = obj.status_history.all()[:10]
        return [
            {
                'from_status': h.from_status,
                'to_status': h.to_status,
                'note': h.note,
                'created_at': h.created_at
            }
            for h in history
        ]



class BookingStatusUpdateSerializer(serializers.Serializer):
    """For status updates with optional fields"""
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    final_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
