from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUserOrProfessionalOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "professional")
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "admin":
            return True

        if request.user.role == "professional":
            return obj.professional.user == request.user

        return False


class IsProfessionalOwnerOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            # return False
            return request.method in SAFE_METHODS

        if request.user.role == "customer":
            return request.method in SAFE_METHODS

        return request.user.role in ("admin", "professional")

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return request.method in SAFE_METHODS

        if request.user.role == "admin":
            return True

        if request.user.role == "professional":
            return obj.professional.user == request.user

        if request.user.role == "customer":
            return request.method in SAFE_METHODS

        return False
