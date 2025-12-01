from django.contrib import admin
from django.urls import path
from profile_app.api.views import ProfileView


urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile-list'),

]
