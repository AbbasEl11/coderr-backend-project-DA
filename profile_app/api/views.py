from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..models import Profile
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ProfileBasicSerializer,
    ProfileBusinessSerializer,
    ProfileCustomerSerializer,
    ProfileSerializer
)


class ProfileDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    API view for retrieving and updating user profiles.

    Allows authenticated users to view any profile,
    but only profile owners can update their own profile.
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Profile.objects.all()
    lookup_field = 'pk'

    def get_object(self):
        """
        Retrieve profile by user ID and check permissions.

        Returns:
            Profile: The requested profile instance

        Raises:
            Http404: If profile doesn't exist
            PermissionDenied: If user lacks required permissions
        """
        obj = get_object_or_404(Profile, user_id=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve a profile.

        Args:
            request: HTTP request
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: Profile data
        """
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests to partially update a profile.

        Args:
            request: HTTP request with update data
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: Updated profile data
        """
        return self.partial_update(request, *args, **kwargs)


class ProfileListView(generics.ListAPIView):
    """
    API view for listing user profiles.

    Supports filtering by user type (customer or business).
    Returns different serializer based on requested mode.
    """

    permission_classes = [IsAuthenticated]
    mode = None
    queryset = Profile.objects.all()

    def get_dispatch(self, request, *args, **kwargs):
        """
        Extract mode from kwargs before dispatching.

        Args:
            request: HTTP request
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments including optional 'mode'

        Returns:
            Response: Dispatched request result
        """
        if 'mode' in kwargs:
            self.mode = kwargs.pop('mode')
        return super().get_dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get filtered queryset based on mode.

        Returns:
            QuerySet: Filtered profiles (all, customer, or business)
        """
        query_set = Profile.objects.all()

        if self.mode == 'customer':
            query_set = query_set.filter(type='customer')
        elif self.mode == 'business':
            query_set = query_set.filter(type='business')
        return query_set

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on mode.

        Returns:
            Serializer: ProfileBusinessSerializer, ProfileCustomerSerializer, or ProfileBasicSerializer
        """
        if self.mode == 'business':
            return ProfileBusinessSerializer
        elif self.mode == 'customer':
            return ProfileCustomerSerializer
        return ProfileBasicSerializer
