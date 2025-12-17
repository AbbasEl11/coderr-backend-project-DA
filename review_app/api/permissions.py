from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    """
    Custom permission to only allow customer users to create reviews.
    """

    def has_permission(self, request, view):
        """
        Check if user is authenticated and has customer profile type.

        Args:
            request: HTTP request
            view: View being accessed

        Returns:
            bool: True if user is authenticated customer user
        """
        if not request.user.is_authenticated:
            return False
        try:
            user = User.objects.get(pk=request.user.pk)
            return getattr(user.profile, 'type', None) == 'customer'
        except:
            return False
    

class IsReviewer(BasePermission):
    """
    Custom permission to only allow review authors to modify their reviews.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user is the reviewer of the review.

        Args:
            request: HTTP request
            view: View being accessed
            obj: Review instance being accessed

        Returns:
            bool: True if user is the reviewer
        """
        return obj.reviewer == request.user
