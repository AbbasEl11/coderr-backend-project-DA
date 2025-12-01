from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics, mixins, status


class ProfileView(generics.CreateAPIView):
    pass
