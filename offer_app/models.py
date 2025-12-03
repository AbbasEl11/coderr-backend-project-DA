from django.db import models
from django.contrib.auth.models import User
from django.db.models import Min
# Create your models here.


class Offer(models.Model):
    user = models.ForeignKey(
        User, related_name='offers', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='offers/images/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def min_price(self):
        return self.details.aggregate(min_value=Min('price'))['min_value']

    def min_delivery_time(self):
        return self.details.aggregate(min_value=Min('delivery_time_in_days'))['min_value']

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = [
        ('basic', 'basic'),
        ('standard', 'standard'),
        ('premium', 'premium')
    ]

    offer = models.ForeignKey(
        Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.offer.title} - ({self.offer_type})"
