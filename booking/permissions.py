from rest_framework.permissions import BasePermission



class IsBookingCustomer(BasePermission):
    """Only the customer who created the booking"""
    def has_object_permission(self, request, view, obj):
        return obj.customer.user == request.user
    

class IsBookingProfessional(BasePermission):
    """Only the professional assigned to the booking"""
    def has_object_permission(self, request, view, obj):
        return obj.professional.user == request.user


class IsBookingParticipant(BasePermission):
    """Either customer or professional in the booking"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            obj.customer.user == user or
            obj.professional.user == user
        )
    

