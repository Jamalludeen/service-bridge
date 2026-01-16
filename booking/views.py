from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Booking, BookingStatusHistory
from .serializers import (
    BookingCreateSerializer,
    BookingListSerializer,
    BookingDetailSerializer,
    BookingStatusUpdateSerializer
)
from .permissions import (
    IsBookingCustomer,
    IsBookingProfessional,
    IsBookingParticipant,
    CanAcceptBooking,
    CanStartBooking,
    CanCompleteBooking,
    CanCancelBooking
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
        return BookingDetailSerializer()
    
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
    
    
    

