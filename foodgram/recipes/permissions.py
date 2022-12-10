from rest_framework import permissions


class IsOwnerOrRead(permissions.BasePermission):

    def has_obj_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
