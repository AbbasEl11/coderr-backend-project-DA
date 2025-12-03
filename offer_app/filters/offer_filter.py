from django_filters import rest_framework as filters
from django.db.models import Min

from offer_app.models import Offer


class OfferFilter(filters.FilterSet):
    creator_id = filters.NumberFilter(field_name='user__id')
    min_price = filters.NumberFilter(
        method='min_price_value', lookup_expr='gte')
    max_delivery_time = filters.NumberFilter(
        method='max_delivery_time_value', lookup_expr='lte')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']
