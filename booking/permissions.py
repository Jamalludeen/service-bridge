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
    


class CanAcceptBooking(BasePermission):
    """Professional can accept only PENDING bookings"""
    def has_object_permission(self, request, view, obj):
        return (
            obj.professional.user == request.user and
            obj.status == 'PENDING'
        )
    

class CanStartBooking(BasePermission):
    """Professional can start only ACCEPTED bookings"""
    def has_object_permission(self, request, view, obj):
        return (
            obj.professional.user == request.user and
            obj.status == 'ACCEPTED'
        )
    

class CanCompleteBooking(BasePermission):
    """Professional can complete only IN_PROGREE bokkings"""
    def has_object_permission(self, request, view, obj):
        return (
            obj.professional.user == request.user and 
            obj.status == 'IN_PROGRESS'
        )
    

class CanCancelBooking(BasePermission):
    """Either party can cancel if not completed"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        is_participant = (
            obj.customer.user == user or
            obj.professional.user == user
        )
        can_cancel = obj.status in ['PENDING', 'ACCEPTED']
        return is_participant and can_cancel


    
