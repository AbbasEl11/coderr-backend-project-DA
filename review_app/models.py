from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_made')
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_user')
    rating = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Review by {self.reviewer.username} for {self.business_user.username} - Rating: {self.rating}'  
