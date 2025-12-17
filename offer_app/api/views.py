from django.db.models import Min
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import status, views, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..filters.offer_filter import OfferFilter
from ..models import Offer, OfferDetail
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import OfferDetailSerializer, OfferSerializer


class OfferPagination(PageNumberPagination):
    """
    Custom pagination class for offers.

    Default page size is 1, customizable via page_size query parameter.
    Maximum page size is 100.
    """

    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100


class OffersViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing offers.

    Provides CRUD operations for offers with filtering, searching, and ordering.
    Permissions vary by action: creation requires business user, updates require ownership.
    """

    serializer_class = OfferSerializer
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend,
                       drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_queryset(self):
        """
        Get optimized queryset for offers.

        Returns:
            QuerySet: Offers with related user and details, ordered by update time
        """
        return (Offer.objects.all()
                .select_related('user')
                .prefetch_related('details')
                .order_by('-updated_at')
                )

    def get_permissions(self):
        """
        Get permission classes based on action.

        Returns:
            list: Permission instances for the current action
        """
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
        """
        Save offer with current user as owner.

        Args:
            serializer: Validated offer serializer
        """
        serializer.save(user=self.request.user)


class OfferDetailView(views.APIView):
    """
    API view for retrieving a single offer detail.

    Requires authentication. Returns detailed information about a specific offer tier.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieve a specific offer detail by ID.

        Args:
            request: HTTP request
            pk: Primary key of the offer detail

        Returns:
            Response: Serialized offer detail data

        Raises:
            Http404: If offer detail doesn't exist
        """
        offer_detail = get_object_or_404(OfferDetail, pk=pk)
        serializer = OfferDetailSerializer(offer_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)
