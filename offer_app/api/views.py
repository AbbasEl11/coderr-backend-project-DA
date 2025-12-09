from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.db.models import Min
from rest_framework import viewsets, views, status, filters as drf_filters
from rest_framework.permissions import IsAuthenticated
from offer_app.filters.offer_filter import OfferFilter
from offer_app.models import Offer, OfferDetail
from offer_app.api.serializers import OfferDetailSerializer, OfferSerializer
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from offer_app.api.permissions import IsOfferOwner, IsBusinessUser


class OfferPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100


class OffersViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
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
                .order_by('-updated_at')
                )

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsBusinessUser]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsOfferOwner]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        offer_detail = get_object_or_404(OfferDetail, pk=pk)
        serializer = OfferDetailSerializer(offer_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)
