from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Payment, PaymentHistory
from .serializers import (
    PaymentCreateSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentConfirmSerializer,
)
from .permissions import IsPaymentParticipant



class PaymentViewSet(ModelViewSet):
    """
    ViewSet for managing payments - SIMPLIFIED VERSION

    Endpoints:
    - POST   /payment/              - Initiate payment (Customer)
    - GET    /payment/              - List my payments
    - GET    /payment/{id}/         - Payment details
    - POST   /payment/{id}/confirm/ - Confirm payment received (Admin/Professional)
    - POST   /payment/{id}/release/ - Release to professional (Admin/Customer)
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.request.user

        if user.role == 'customer':
            return Payment.objects.filter(
                booking__customer__user=user
            ).select_related('booking__service', 'booking__professional__user')

        elif user.role == 'professional':
            return Payment.objects.filter(
                booking__professional__user=user
            ).select_related('booking__service', 'booking__customer__user')

        elif user.role == 'admin':
            return Payment.objects.all().select_related(
                'booking__service',
                'booking__professional__user',
                'booking__customer__user'
            )

        return Payment.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'list':
            return PaymentListSerializer
        return PaymentDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """Initiate a payment for a booking"""
        if request.user.role != 'customer':
            return Response(
                {"error": "Only customers can initiate payments."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    def _update_status(self, payment, new_status, user, note='', **extra_fields):
        """Helper to update status with history tracking"""
        old_status = payment.status
        payment.status = new_status

        for field, value in extra_fields.items():
            setattr(payment, field, value)

        payment.save()

        PaymentHistory.objects.create(
            payment=payment,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            note=note
        )

        return payment
    
    @action(detail=True, methods=['POST'])
    def confirm(self, request, pk=None):
        """
        Confirm payment received - moves to HELD.
        For CASH: Professional confirms cash received
        For MOBILE_MONEY/BANK_TRANSFER: Admin confirms after verifying transaction
        """
        payment = self.get_object()

        # Check permissions
        if request.user.role == 'admin':
            # Admin can confirm any payment
            pass
        elif payment.payment_method == 'CASH':
            # Professional can confirm CASH payments
            if payment.booking.professional.user != request.user:
                return Response(
                    {"error": "Only assigned professional can confirm cash payments."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            # Only admin can confirm non-cash payments
            return Response(
                {"error": "Only admin can confirm non-cash payments."},
                status=status.HTTP_403_FORBIDDEN
            )

        if payment.status != 'PENDING':
            return Response(
                {"error": f"Cannot confirm payment with status {payment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PaymentConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self._update_status(
            payment, 'HELD', request.user,
            note='Payment confirmed and held',
            external_transaction_id=serializer.validated_data.get(
                'external_transaction_id', ''
            ),
            notes=serializer.validated_data.get('notes', '')
        )

        return Response({
            "message": "Payment confirmed and held.",
            "data": PaymentDetailSerializer(payment).data
        })
    
    @action(detail=True, methods=['POST'])
    def release(self, request, pk=None):
        """
        Release payment to professional.
        Can be called by admin or customer after booking is completed.
        """
        payment = self.get_object()

        # Check permissions
        if request.user.role == 'admin':
            # Admin can release any payment
            pass
        elif payment.booking.customer.user == request.user:
            # Customer can release their own payment
            pass
        else:
            return Response(
                {"error": "Only admin or customer can release payment."},
                status=status.HTTP_403_FORBIDDEN
            )

        if payment.status != 'HELD':
            return Response(
                {"error": f"Cannot release payment with status {payment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if payment.booking.status != 'COMPLETED':
            return Response(
                {"error": "Cannot release payment for incomplete booking."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self._update_status(
            payment, 'RELEASED', request.user,
            note='Payment released to professional'
        )

        # TODO: Trigger actual payout to professional (when payment gateway integrated)

        return Response({
            "message": "Payment released to professional.",
            "data": PaymentDetailSerializer(payment).data
        })
    
    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        """
        Cancel a payment.
        Can be called by customer if payment is still PENDING.
        """
        payment = self.get_object()

        # Only customer can cancel
        if payment.booking.customer.user != request.user:
            return Response(
                {"error": "Only the customer can cancel payment."},
                status=status.HTTP_403_FORBIDDEN
            )

        if payment.status != 'PENDING':
            return Response(
                {"error": f"Cannot cancel payment with status {payment.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cancellation_reason = request.data.get('notes', '')

        self._update_status(
            payment, 'CANCELLED', request.user,
            note=f'Payment cancelled: {cancellation_reason}',
            notes=cancellation_reason
        )

        return Response({
            "message": "Payment cancelled successfully.",
            "data": PaymentDetailSerializer(payment).data
        })