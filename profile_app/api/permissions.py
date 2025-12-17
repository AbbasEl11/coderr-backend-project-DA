from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to allow read access to any profile but only allow owners to modify.

    Authenticated users can view any profile (GET requests).
    Only the profile owner can modify their own profile (PATCH/PUT/DELETE).
    """

    message = "You must be the owner of this profile to modify it."

    def has_permission(self, request, view):
        """
        Check if user is authenticated.

        Args:
            request: HTTP request
            view: View being accessed

        Returns:
            bool: True if user is authenticated
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the profile object.

        Args:
            request: HTTP request
            view: View being accessed
            obj: Profile object being accessed

        Returns:
            bool: True if safe method or user is profile owner
        """
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
