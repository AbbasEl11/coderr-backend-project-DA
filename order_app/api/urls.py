from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from order_app.api.views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    #     path('offerdetails/<int:pk>/', OfferDetailView.as_view(), name='offer-details'),
]
