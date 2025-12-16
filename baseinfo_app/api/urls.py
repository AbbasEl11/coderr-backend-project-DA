from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from baseinfo_app.api.views import BaseInfoView



urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]
