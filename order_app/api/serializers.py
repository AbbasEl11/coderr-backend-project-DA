from rest_framework.reverse import reverse
from rest_framework import serializers
from order_app.models import Order
from django.contrib.auth.models import User
from offer_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(), source='offer_detail')

    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(
        source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(
        source='offer_detail.delivery_time_in_days', read_only=True)
    price = serializers.IntegerField(
        source='offer_detail.price', read_only=True)
    features = serializers.CharField(
        source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(
        source='offer_detail.offer_type', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'offer_detail_id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'created_at', 'updated_at', 'title',
                            'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def create(self, validated_data):
        request = self.context.get('request')
        offer_detail = validated_data['offer_detail']
        validated_data['business_user'] = offer_detail.offer.user
        validated_data['customer_user'] = request.user
        order = Order.objects.create(**validated_data)
        return order

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')

        action = getattr(view, 'action', None) if view else None
        data.pop('offer_detail_id', None)

        if request and request.method == 'POST' and action == 'create':
            data.pop('updated_at', None)

            return data

        return data
