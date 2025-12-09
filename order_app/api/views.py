from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.db.models import Q
from rest_framework import viewsets
from order_app.api.serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from order_app.models import Order


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = None

    def get_queryset(self):
        action = self.action

        if action == 'list':
            return Order.objects.filter(
                Q(customer_user=self.request.user) | Q(
                    business_user=self.request.user)
            )
        else:
            return Order.objects.all()
