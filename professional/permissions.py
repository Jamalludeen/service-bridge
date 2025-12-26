from rest_framework.permissions import BasePermission


class IsProfessionalUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'professional'
    

class IsProfessionalOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        
        if request.user.role == 'professional':
            result = obj.user == request.user
            return result
        
        return False
    