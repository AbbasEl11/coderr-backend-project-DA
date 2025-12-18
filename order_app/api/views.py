from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from ..models import Order
from .permissions import IsBusiness, IsCustomer
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.

    Provides CRUD operations with role-based permissions.
    Customers can create orders, business users can update status, admins can delete.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = None

    def initial(self, request, *args, **kwargs):
        """
        Runs before any action - checks if order exists before permission check.
        
        Raises:
            Http404: If order doesn't exist (before permission check)
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            pk = self.kwargs.get('pk')
            if pk:
                get_object_or_404(Order, pk=pk)
        super().initial(request, *args, **kwargs)

    def get_permissions(self):
        """
        Get permission classes based on action.

        Returns:
            list: Permission instances for the current action
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsCustomer]
        elif self.action in ['update', 'partial_update',]:
            self.permission_classes = [IsAuthenticated, IsBusiness]
        elif self.action == 'destroy':
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Get filtered queryset based on action and user.

        Returns:
            QuerySet: Orders filtered by user involvement (customer or business)
        """
        action = self.action

        if action == 'list':
            return Order.objects.filter(
                Q(customer_user=self.request.user) | Q(
                    business_user=self.request.user)
            )
        else:
            return Order.objects.all()
        
class CountOrdersView(views.APIView):
    """
    API view to count in-progress orders for a business user.

    Returns the number of orders with 'in_progress' status for the specified business user.
    """

    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Get count of in-progress orders for a business user.

        Args:
            request: HTTP request
            pk: User ID of the business user

        Returns:
            Response: JSON with order_count field

        Raises:
            Http404: If user doesn't exist or is not a business user
        """
        user = get_object_or_404(User, pk=pk)

        if user.profile.type != 'business':
            return Response({'detail': 'User is not a business user.'}, status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(business_user=user, status = 'in_progress').count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)



class CompletedOrdersCountView(views.APIView):
    """
    API view to count completed orders for a business user.

    Returns the number of orders with 'completed' status for the specified business user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Get count of completed orders for a business user.

        Args:
            request: HTTP request
            pk: User ID of the business user

        Returns:
            Response: JSON with completed_order_count field

        Raises:
            Http404: If user doesn't exist or is not a business user
        """
        user = get_object_or_404(User, pk=pk)

        if user.profile.type != 'business':
            return Response({'detail': 'User is not a business user.'}, status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(business_user=user, status = 'completed').count()
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)