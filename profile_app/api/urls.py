from django.contrib import admin
from django.urls import path

from profile_app.api.views import ProfileDetailView, ProfileListView


urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', ProfileListView.as_view(mode="business"),
         name='profile-business'),
    path('profiles/customer/', ProfileListView.as_view(mode="customer",),
         name='profile-customer'),
]
