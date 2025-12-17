from django.db.models import Min
from django_filters import rest_framework as filters

from review_app.models import Review


class ReviewFilter(filters.FilterSet):
    """
    Filter set for Review model.

    Provides filtering by business user ID and reviewer ID.
    """

    business_user = filters.NumberFilter(field_name='business_user__id')
    reviewer_id = filters.NumberFilter(field_name='reviewer__id')

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']
