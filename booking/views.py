from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Booking, BookingStatusHistory
from .serializers import (
    BookingCreateSerializer,
    BookingListSerializer,
    BookingDetailSerializer,
    BookingStatusUpdateSerializer
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
    
    
