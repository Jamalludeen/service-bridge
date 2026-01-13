from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsProfessionalOwnerOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Customers: read-only access
        if request.user.role == "customer":
            return request.method in SAFE_METHODS

        # Admin & professional
        return request.user.role in ("admin", "professional")

    def has_object_permission(self, request, view, obj):
        # Admin: full access
        if request.user.role == "admin":
            return True

        # Professional: only own services
        if request.user.role == "professional":
            return obj.professional.user == request.user

        # Customer: read-only
        if request.user.role == "customer":
            return request.method in SAFE_METHODS

        return False
