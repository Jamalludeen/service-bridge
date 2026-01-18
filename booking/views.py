from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from .models import Booking, BookingStatusHistory
from .filters import MyBookingFilter
from .serializers import (
    BookingCreateSerializer,
    BookingListSerializer,
    BookingDetailSerializer,
    BookingStatusUpdateSerializer,
    BookingStatusHistorySerializer
)
from .permissions import (
    IsBookingCustomer,
    IsBookingProfessional,
    IsBookingParticipant,
    CanAcceptBooking,
    CanStartBooking,
    CanCompleteBooking,
    CanCancelBooking,
    CanViewBookingHistory
)



class BookingViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'customer':
            return Booking.objects.filter(
                customer__user=user
            ).select_related('service', 'professional')
        
        elif user.role == 'professional':
            return Booking.objects.filter(
                professional__user=user
            ).select_related('service', 'customer__user')
        
        elif user.role == 'admin':
            return Booking.objects.all().select_related(
                'service', 'professional__user', 'customer__user'
            )
        
        return Booking.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'list':
            return BookingListSerializer
        elif self.action == 'my_bookings':
            return BookingListSerializer
        return BookingDetailSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # only customers can create bookings
            return [IsAuthenticated()]
        elif self.action is ['retrieve', 'list']:
            return [IsAuthenticated(), IsBookingParticipant]
        return super().get_permissions()


    def create(self, request, *args, **kwargs):
        if request.user.role != 'customer':
            return Response(
                {"error": "Only customers can create bookings."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)

    def _update_status(self, booking, new_status, user, note='', **extra_fields):
        """Helper to update status with history tracking"""
        old_status = booking.status
        booking.status = new_status

        for field, value in extra_fields.items():
            setattr(booking, field, value)
        booking.save()

        BookingStatusHistory.objects.create(
            booking=booking,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            note=note
        )

        return booking
    
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated, CanAcceptBooking])
    def accept(self, request, pk=None):
        """Professional accepts a booking"""
        booking = self.get_object()
        professioanl_info = booking.professional.user.get_full_name() or booking.professional.user.username
        self._update_status(
            booking, 'ACCEPTED',request.user, 
            note=f'Booking accepted by {professioanl_info}',
            accepted_at=timezone.now()
        )
        return Response({
            "message": "Booking accepted successfully.",
            "data": BookingDetailSerializer(booking).data
        })
    
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated, CanAcceptBooking])
    def reject(self, request, pk=None):
        """Professional can rejects a booking"""
        booking = self.get_object()
        serializer = BookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reason = serializer.validated_data.get('rejection_reason', '')
        user_info = request.user.get_full_name() or request.user.username

        self._update_status(
            booking, 'REJECTED', request.user,
            note=f'Booking rejected: {reason} by {user_info}',
            rejection_reason=reason
        )
        return Response({
            "message": "Booking rejected.",
            "data": BookingDetailSerializer(booking).data
        })

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated, CanStartBooking])
    def start(self, request, pk=None):
        """Professional starts work on booking"""
        booking = self.get_object()
        professioanl_info = booking.professional.user.get_full_name() or booking.professional.user.username

        self._update_status(
            booking, 'IN_PROGRESS', request.user,
            note=f'Work started by {professioanl_info}',
            started_at=timezone.now()
        )
        return Response({
            "message": "Booking started.",
            "data": BookingDetailSerializer(booking).data
        })
    
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated, CanCompleteBooking])
    def complete(self, request, pk=None):
        """Professional completes the booking"""
        booking = self.get_object()
        serializer = BookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        final_price = serializer.validated_data.get(
            'final_price', booking.estimated_price
        )

        self._update_status(
            booking, 'COMPLETED', request.user,
            note='Work completed',
            completed_at=timezone.now(),
            final_price=final_price
        )

        # update customer's total_bookings count
        booking.customer.total_bookings += 1
        booking.customer.save(update_fields=['total_bookings'])

        return Response({
            "message": "Booking completed successfully.",
            "data": BookingDetailSerializer(booking).data
        })
    
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated, CanCancelBooking])
    def cancel(self, request, pk=None):
        """Either party cancels the booking"""
        booking = self.get_object()
        serializer = BookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reason = serializer.validated_data.get('cancellation_reason', '')
        user_info = request.user.get_full_name() or request.user.username

        self._update_status(
            booking, 'CANCELLED', request.user,
            note=f'Cancelled: {reason} by {user_info}',
            cancellation_reason=reason,
            cancelled_by=request.user
        )
        return Response({
            "message": "Booking cancelled.",
            "data": BookingDetailSerializer(booking).data
        })
    
    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated, CanViewBookingHistory])
    def history(self, request, pk=None):
        booking = self.get_object()
        histories = BookingStatusHistory.objects.filter(
            booking=booking
        )
        serializer = BookingStatusHistorySerializer(histories,many=True)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated, CanViewBookingHistory])
    def my_bookings(self, request):
        user = request.user
        bookings = Booking.objects.all()

        if user.role == 'professional':
            bookings = bookings.filter(professional__user=user)
        
        elif user.role == 'customer':
            bookings = bookings.filter(customer__user=user)
        
        elif user.role == 'admin':
            pass

        filterset = MyBookingFilter(
            data=request.query_params,
            queryset=bookings
        )   

        if not filterset.is_valid():
            return Response(
                filterset.errors,
                status=status.HTTP_400_BAD_REQUEST
        )

        serializer = self.get_serializer(filterset.qs, many=True)

        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK
        )
                
        
