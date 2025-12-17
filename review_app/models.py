from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    """
    Model representing a customer review for a business user.

    Links a customer reviewer to a business user with a rating and description.
    Tracks creation and update timestamps.
    """

    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_made')
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_user')
    rating = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']    
    def __str__(self):
        """
        Return string representation of the review.

        Returns:
            str: Review summary with reviewer, business user, and rating
        """
        return f'Review by {self.reviewer.username} for {self.business_user.username} - Rating: {self.rating}'  
