from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    User profile model extending Django's User model.

    Stores additional user information including personal details,
    contact information, and user type (customer or business).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    file = models.FileField(upload_to='profiles/', null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    tel = models.CharField(max_length=15, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    working_hours = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, choices=[(
        'customer', 'customer'), ('business', 'business')], default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-created_at']