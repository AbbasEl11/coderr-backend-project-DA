from django.db import models
from django.contrib.auth.models import User
from django.db.models import Min


class Offer(models.Model):
    """
    Model representing a service offer created by a business user.

    Contains basic offer information and related offer details.
    Provides methods to calculate minimum price and delivery time.
    """

    user = models.ForeignKey(
        User, related_name='offers', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='offers/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def min_price(self):
        """
        Get the minimum price across all offer details.

        Returns:
            int: Minimum price or None if no details exist
        """
        return self.details.aggregate(min_value=Min('price'))['min_value']

    def min_delivery_time(self):
        """
        Get the minimum delivery time across all offer details.

        Returns:
            int: Minimum delivery time in days or None if no details exist
        """
        return self.details.aggregate(min_value=Min('delivery_time_in_days'))['min_value']

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
        ordering = ['-created_at']

    def __str__(self):
        """
        Return string representation of the offer.

        Returns:
            str: Offer title
        """
        return self.title


class OfferDetail(models.Model):
    """
    Model representing detailed pricing tiers for an offer.

    Each offer can have multiple details representing different service levels
    (basic, standard, premium) with varying prices and features.
    """

    OFFER_TYPE_CHOICES = [
        ('basic', 'basic'),
        ('standard', 'standard'),
        ('premium', 'premium')
    ]

    offer = models.ForeignKey(
        Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField()
    price = models.PositiveIntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=20, choices=OFFER_TYPE_CHOICES)

    class Meta:
        verbose_name = 'Offer Detail'
        verbose_name_plural = 'Offer Details'
        ordering = ['offer', 'offer_type']

    def __str__(self):
        """
        Return string representation of the offer detail.

        Returns:
            str: Offer title with type in parentheses
        """
        return f"{self.offer.title} - ({self.offer_type})"
