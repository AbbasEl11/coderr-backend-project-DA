from django.db import models
from django.contrib.auth.models import User
from offer_app.models import OfferDetail
# Create your models here.


class Order(models.Model):
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
