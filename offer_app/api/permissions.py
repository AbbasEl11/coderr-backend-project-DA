from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

from django.contrib.auth.models import User


class IsOfferOwner(BasePermission):
    """
    Custom permission to only allow owners of an offer to access or edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Assuming 'obj' is an instance of Offer
        return obj.user == request.user


class IsBusinessUser(BasePermission):
    """
    Custom permission to only allow business users to create offers.
    """

    def has_permission(self, request, view):
        user = User.objects.get(pk=request.user.pk)
        return request.user.is_authenticated and getattr(user.profile, 'type', None) == 'business'
