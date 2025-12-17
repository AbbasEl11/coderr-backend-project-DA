from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework import generics, mixins, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from offer_app.models import Offer
from profile_app.models import Profile
from review_app.models import Review

class BaseInfoView(mixins.ListModelMixin, generics.GenericAPIView):
    """
    API view for retrieving basic platform statistics.

    Provides aggregated data including review count, average rating,
    business profile count, and offer count. Accessible without authentication.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Get platform statistics.

        Args:
            request: HTTP request
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            Response: JSON with review_count, average_rating, business_profile_count, offer_count
        """
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