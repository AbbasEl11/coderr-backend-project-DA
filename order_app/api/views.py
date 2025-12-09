from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.db.models import Min
from rest_framework import viewsets
from order_app.api.serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from order_app.models import Order


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
