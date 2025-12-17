from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics, mixins, status
from django.db.models import Avg
from review_app.models import Review
from profile_app.models import Profile
from offer_app.models import Offer

class BaseInfoView(mixins.ListModelMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        review_count = Review.objects.all().count()
        average_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        business_profile_count = Profile.objects.filter(type='business').count()
        offer_count = Offer.objects.all().count()
        
        data = {
            'review_count': review_count,
            'average_rating': round(average_rating, 2),
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)