from rest_framework.permissions import BasePermission

#Currently not used
class IsPcOwnerOrCustomizedFalse(BasePermission):
    """
    Grants access for all if the `is_customized` field is False.
    If is_customized is True only the user owner has access.
    """
    def has_object_permission(self, request, view, obj):
        if obj.is_customized == False:
            return True
        if obj.is_customized == True:
            if obj.id == request.user.id: # Owner would need to be the Foreign key from user.
                return True
        return False

