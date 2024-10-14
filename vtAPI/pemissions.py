from rest_framework import permissions


class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role is not "EMPLOYEE":
            return False
        
        return True