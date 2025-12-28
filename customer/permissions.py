from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsCustomerOwner(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.user.role == "admin":
            return True
        
        if request.user.role == "customer":
            result = obj.user == request.user
            return result

        return False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'
    