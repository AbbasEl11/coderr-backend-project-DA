from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import viewsets
from review_app.api.serializers import ReviewSerializer
from review_app.models import Review
from review_app.api.permissions import IsCustomer, IsReviewer

from ..filters.review_filter import ReviewFilter

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    filterset_class = ReviewFilter
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']

    def get_queryset(self):
        return (Review.objects.all()
                .order_by('-updated_at')
                )


    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsCustomer]
        elif self.action in ['update', 'partial_update','destroy']:
            self.permission_classes = [IsAuthenticated, IsReviewer]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    