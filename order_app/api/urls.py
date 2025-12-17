from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from order_app.api.views import CountOrdersView, CompletedOrdersCountView, OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('order-count/<int:pk>/', CountOrdersView.as_view(), name='order-count-details'),
    path('completed-order-count/<int:pk>/', CompletedOrdersCountView.as_view(), name='completed-order-count-details'),
]
