from django.contrib import admin
from django.urls import path

from auth_app.api.views import RegistrationView, LoginView

urlpatterns = [
    # User registration endpoint
    path('registration/', RegistrationView.as_view(), name='registration'),

    # User login endpoint
    path('login/', LoginView.as_view(), name='login'),
]
