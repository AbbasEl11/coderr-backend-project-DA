from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from offer_app.api.views import OffersViewSet, OfferDetailView

router = DefaultRouter()
router.register(r'offers', OffersViewSet, basename='offers')

urlpatterns = [
    path('', include(router.urls)),
    path('offerdetails/<int:pk>/', OfferDetailView.as_view(), name='offer-details'),
]
