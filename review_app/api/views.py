from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..filters.review_filter import ReviewFilter
from ..models import Review
from .permissions import IsCustomer, IsReviewer
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.

    Provides CRUD operations with filtering and ordering capabilities.
    Customers can create reviews, only reviewers can update/delete their own reviews.
    """

    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']

    def get_queryset(self):
        """
        Get queryset for reviews ordered by update time.

        Returns:
            QuerySet: Reviews ordered by most recent first
        """
        return (Review.objects.all()
                .order_by('-updated_at')
                )


    def get_permissions(self):
        """
        Get permission classes based on action.

        Returns:
            list: Permission instances for the current action
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsCustomer]
        elif self.action in ['update', 'partial_update','destroy']:
            self.permission_classes = [IsAuthenticated, IsReviewer]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Save review with current user as reviewer.

        Args:
            serializer: Validated review serializer
        """
        serializer.save(reviewer=self.request.user)

    