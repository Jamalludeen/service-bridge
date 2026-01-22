from rest_framework import serializers
from decimal import Decimal
from .models import Payment, PaymentHistory


class PaymentCreateSerializer(serializers.ModelSerializer):
    """For initiating a payment"""
    booking_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = ['booking_id', 'payment_method']  # REMOVED: currency

    def validate_booking_id(self, value):
        from booking.models import Booking

        try:
            booking = Booking.objects.get(id=value)
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found.")

        # Check if payment already exists
        if hasattr(booking, 'payment'):
            raise serializers.ValidationError(
                "Payment already exists for this booking."
            )

        # Check booking status
        if booking.status not in ['ACCEPTED', 'IN_PROGRESS']:
            raise serializers.ValidationError(
                "Payment can only be initiated for accepted bookings."
            )

        # Check if user is the customer
        user = self.context['request'].user
        if booking.customer.user != user:
            raise serializers.ValidationError(
                "Only the booking customer can initiate payment."
            )

        return value

    def create(self, validated_data):
        from booking.models import Booking

        booking_id = validated_data.pop('booking_id')
        booking = Booking.objects.get(id=booking_id)

        # Use final_price if available, otherwise estimated_price
        amount = booking.final_price or booking.estimated_price

        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            **validated_data
        )

        # Create initial history
        PaymentHistory.objects.create(
            payment=payment,
            to_status='PENDING',
            changed_by=self.context['request'].user,
            note='Payment initiated'
        )

        return payment


class PaymentListSerializer(serializers.ModelSerializer):
    """For listing payments"""
    booking_id = serializers.IntegerField(source='booking.id')
    service_title = serializers.CharField(source='booking.service.title')

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'booking_id', 'service_title',
            'amount', 'payment_method', 'status', 'created_at'
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    """For detailed payment view"""
    booking_id = serializers.IntegerField(source='booking.id')
    service_title = serializers.CharField(source='booking.service.title')
    customer_name = serializers.SerializerMethodField()
    professional_name = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'booking_id', 'service_title',
            'customer_name', 'professional_name',
            'amount', 'payment_method', 'status',
            'external_transaction_id', 'notes',
            'created_at', 'updated_at', 'history'
        ]
        # REMOVED: currency, platform_fee_*, escrow_held_at, released_at, refunded_at

    def get_customer_name(self, obj):
        return obj.booking.customer.user.get_full_name() or obj.booking.customer.user.email

    def get_professional_name(self, obj):
        return obj.booking.professional.user.get_full_name() or obj.booking.professional.user.email

    def get_history(self, obj):
        history = obj.history.all()[:10]
        return [
            {
                'from_status': h.from_status,
                'to_status': h.to_status,
                'note': h.note,
                'created_at': h.created_at,
                'changed_by': h.changed_by.email if h.changed_by else None
            }
            for h in history
        ]



class PaymentConfirmSerializer(serializers.Serializer):
    """For confirming payment received (move to HELD)"""
    external_transaction_id = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Transaction ID from external payment gateway"
    )
    notes = serializers.CharField(required=False, allow_blank=True)
