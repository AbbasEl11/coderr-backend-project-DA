from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

class IsBusiness(BasePermission):
    """
    Custom permission to only allow business users to update orders.
    """

    def has_permission(self, request, view):
        """
        Check if user is authenticated and has business profile type.

        Args:
            request: HTTP request
            view: View being accessed

        Returns:
            bool: True if user is authenticated business user
        """
        user = User.objects.get(pk=request.user.pk)
        return request.user.is_authenticated and getattr(user.profile, 'type', None) == 'business'
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the business user associated with the order.

        Args:
            request: HTTP request
            view: View being accessed
            obj: Order instance being accessed

        Returns:
            bool: True if user is the business user of the order
        """
        return obj.business_user == request.user

class IsCustomer(BasePermission):
    """
    Custom permission to only allow customer users to create orders.
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
        user = User.objects.get(pk=request.user.pk)
        return request.user.is_authenticated and getattr(user.profile, 'type', None) == 'customer'

