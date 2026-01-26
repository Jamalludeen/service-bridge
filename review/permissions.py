from rest_framework.permissions import BasePermission


class IsReviewOwner(BasePermission):
    """Only the review owner (customer) can update/delete"""

    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user


class IsProfessionalOfReview(BasePermission):
    """Only the professional being reviewed can respond"""

    def has_object_permission(self, request, view, obj):
        return obj.professional.user == request.user
