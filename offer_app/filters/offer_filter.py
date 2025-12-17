from django.db.models import Min
from django_filters import rest_framework as filters

from offer_app.models import Offer


class OfferFilter(filters.FilterSet):
    """
    Filter set for Offer model.

    Provides filtering by creator ID, minimum price, and maximum delivery time.
    """

    creator_id = filters.NumberFilter(field_name='user__id')
    min_price = filters.NumberFilter(
        method='min_price_value', lookup_expr='gte')
    max_delivery_time = filters.NumberFilter(
        method='max_delivery_time_value', lookup_expr='lte')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def min_price_value(self, queryset, name, value):
        """
        Filter offers by minimum price.

        Args:
            queryset: Offer queryset to filter
            name: Field name (unused)
            value: Minimum price threshold

        Returns:
            QuerySet: Filtered offers with min_price >= value
        """
        return queryset.annotate(
            min_price_val=Min('details__price')
        ).filter(min_price_val__gte=value)

    def max_delivery_time_value(self, queryset, name, value):
        """
        Filter offers by maximum delivery time.

        Args:
            queryset: Offer queryset to filter
            name: Field name (unused)
            value: Maximum delivery time threshold in days

        Returns:
            QuerySet: Filtered offers with min_delivery_time <= value
        """
        return queryset.annotate(
            min_delivery_time_val=Min('details__delivery_time_in_days')
        ).filter(min_delivery_time_val__lte=value)
