from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from rest_framework import viewsets, views
from order_app.api.serializers import OrderSerializer
from rest_framework.response import Response
from order_app.models import Order
from order_app.api.permissions import IsCustomer, IsBusiness
from django.contrib.auth.models import User


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = None

    def get_permissions(self):
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
        action = self.action

        if action == 'list':
            return Order.objects.filter(
                Q(customer_user=self.request.user) | Q(
                    business_user=self.request.user)
            )
        else:
            return Order.objects.all()
        
class CountOrdersView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user.profile.type != 'business':
            return Response({'detail': 'User is not a business user.'}, status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(business_user=user, status = 'in_progress').count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)



class CompletedOrdersCountView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        user = get_object_or_404(User, pk=pk)

        if user.profile.type != 'business':
            return Response({'detail': 'User is not a business user.'}, status=status.HTTP_404_NOT_FOUND)

        count = Order.objects.filter(business_user=user, status = 'completed').count()
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)