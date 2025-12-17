from django.contrib.auth.models import User
from rest_framework import generics, mixins, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegistrationSerializer, LoginSerializer


class RegistrationView(generics.CreateAPIView):
    """
    API view for user registration.

    Allows any user to register by providing username, email, password,
    repeated_password, and user type (customer or business).
    Returns an authentication token upon successful registration.
    """

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def create(self, request):
        """
        Create a new user account.

        Args:
            request: HTTP request containing user registration data

        Returns:
            Response: JSON containing authentication token, username, email, and user_id

        Raises:
            ValidationError: If registration data is invalid
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        saved_account = serializer.save()
        token, created = Token.objects.get_or_create(user=saved_account)

        response_data = {
            'token': token.key,
            'username': saved_account.username,
            'email': saved_account.email,
            'user_id': saved_account.id
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """
    API view for user authentication.

    Allows any user to login by providing username and password.
    Returns an authentication token upon successful login.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Authenticate user and return authentication token.

        Args:
            request: HTTP request containing login credentials
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: JSON containing authentication token, username, email, and user_id

        Raises:
            ValidationError: If credentials are invalid
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.get()
        token, created = Token.objects.get_or_create(user=user)

        response_data = {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }

        return Response(response_data, status=status.HTTP_200_OK)
