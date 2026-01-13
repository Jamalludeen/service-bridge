from rest_framework.permissions import BasePermission

class IsProfessionalOwnerOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Must be authenticated AND role must be valid
        return (
            request.user.is_authenticated and
            request.user.role in ("admin", "professional")
        )

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True

        if request.user.role == "professional":
            return obj.professional.user == request.user

        return False
