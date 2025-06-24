from rest_framework.permissions import BasePermission


class IsUserOwner(BasePermission):
    """If the user is owner of the data he can request it."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.id == request.user.id


