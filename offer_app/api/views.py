from rest_framework.permissions import AllowAny
from django.db.models import Min
from rest_framework import viewsets, filters as drf_filters
from rest_framework.permissions import IsAuthenticated
from offer_app.filters.offer_filter import OfferFilter
from offer_app.models import Offer
from offer_app.api.serializers import OfferSerializer
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


class OfferPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100


class OffersViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend,
                       drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_queryset(self):
        return (Offer.objects.all()
                .select_related('user')
                .prefetch_related('details')
                )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
