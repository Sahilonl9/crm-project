from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Allow access only to the owner of the object."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        if hasattr(obj, "lead"):
            return obj.lead.owner == request.user

        return False
