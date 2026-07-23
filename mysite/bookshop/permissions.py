from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'email') and request.user.is_authenticated:
            return obj.email == request.user.email

        return request.user and request.user.is_staff