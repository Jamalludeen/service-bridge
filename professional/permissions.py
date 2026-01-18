from rest_framework.permissions import BasePermission


class IsProfessionalUser(BasePermission):
    def has_permission(self, request, view):
        # Ensure we don't access `role` on AnonymousUser
        if not getattr(request, 'user', None):
            return False
        if not getattr(request.user, 'is_authenticated', False):
            return False
        return getattr(request.user, 'role', None) == 'professional'
    

class IsProfessionalOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Defensive checks for anonymous users
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return False

        role = getattr(user, 'role', None)
        if role == 'admin':
            return True

        if role == 'professional':
            return obj.user == user

        return False
    