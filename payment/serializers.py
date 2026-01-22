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
