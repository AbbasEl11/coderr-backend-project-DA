from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework import generics, mixins
from profile_app.api.serializers import ProfileBasicSerializer, ProfileBusinessSerializer, ProfileCustomerSerializer, ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from ..models import Profile


class ProfileDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    lookup_field = 'pk'

    def get_object(self):
        return get_object_or_404(Profile, user_id=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated]
        return self.partial_update(request, *args, **kwargs)


class ProfileListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    mode = None
    queryset = Profile.objects.all()

    def get_dispatch(self, request, *args, **kwargs):
        if 'mode' in kwargs:
            self.mode = kwargs.pop('mode')
        return super().get_dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query_set = Profile.objects.all()

        if self.mode == 'customer':
            query_set = query_set.filter(type='customer')
        elif self.mode == 'business':
            query_set = query_set.filter(type='business')
        return query_set

    def get_serializer_class(self):
        if self.mode == 'business':
            return ProfileBusinessSerializer
        elif self.mode == 'customer':
            return ProfileCustomerSerializer
        return ProfileBasicSerializer
