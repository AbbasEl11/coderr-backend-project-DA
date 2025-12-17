from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission


class IsOfferOwner(BasePermission):
    """
    Custom permission to only allow owners of an offer to access or edit it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user is the owner of the offer.

        Args:
            request: HTTP request
            view: View being accessed
            obj: Offer instance being accessed

        Returns:
            bool: True if user is the offer owner
        """
        return obj.user == request.user


class IsBusinessUser(BasePermission):
    """
    Custom permission to only allow business users to create offers.
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
