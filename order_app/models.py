from django.db import models
from django.contrib.auth.models import User
from offer_app.models import OfferDetail


class Order(models.Model):
    """
    Model representing an order placed by a customer for an offer detail.

    Links a customer to a business user through an offer detail.
    Tracks order status (in_progress, completed, canceled).
    """

    offer_detail = models.ForeignKey(
        OfferDetail, on_delete=models.CASCADE, related_name='orders')
    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customer_orders')
    business_user = models.ForeignKey(
        User,  on_delete=models.CASCADE, related_name='business_orders')

    status_choices = [
        ('in_progress', 'in_progress'),
        ('completed', 'completed'),
        ('canceled', 'canceled'),
    ]

    status = models.CharField(
        max_length=20, choices=status_choices, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
