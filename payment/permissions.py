
from rest_framework.permissions import BasePermission


class IsPaymentCustomer(BasePermission):
    """Only the customer who owns the booking/payment"""
    def has_object_permission(self, request, view, obj):
        return obj.booking.customer.user == request.user


class IsPaymentProfessional(BasePermission):
    """Only the professional assigned to the booking"""
    def has_object_permission(self, request, view, obj):
        return obj.booking.professional.user == request.user


class IsPaymentParticipant(BasePermission):
    """Either customer or professional"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            obj.booking.customer.user == user or
            obj.booking.professional.user == user
        )