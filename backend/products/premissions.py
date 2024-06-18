from rest_framework.permissions import BasePermission

class IsAdminOrGS(BasePermission):
    """
    Custom permission to only allow superusers or users with the GS position to create products.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        # Allow superusers
        if request.user.is_superuser:
            return True
        # Allow users with the GS position
        return request.user.position == 'GS'
