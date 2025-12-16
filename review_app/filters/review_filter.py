from django_filters import rest_framework as filters
from django.db.models import Min

from review_app.models import Review


class ReviewFilter(filters.FilterSet):
    business_user = filters.NumberFilter(field_name='business_user__id')
    reviewer_id = filters.NumberFilter(field_name='reviewer__id')

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']
