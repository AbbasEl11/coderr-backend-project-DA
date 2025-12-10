from rest_framework.reverse import reverse
from rest_framework import serializers
from order_app.models import Order
from django.contrib.auth.models import User
from offer_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(), source='offer_detail', error_messages={
            'does_not_exist': 'Offer detail with the given ID does not exist.'})

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
    
    status = serializers.CharField(required=False)
    
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
        read_only_fields = ['id', 'customer_user', 'business_user', 'created_at', 'updated_at', 'tite',
                            'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def validate(self, attrs):
        attrs = super().validate(attrs)

        request = self.context.get('request')
        view = self.context.get('view')
        method = getattr(request, 'method', None) 
        action = getattr(view, 'action', None)
        initial = self.initial_data or {}

        if method == 'POST' and action == 'create':
            allowed = required = {'offer_detail_id'}
        elif method == 'PATCH' and action == 'partial_update':
            allowed = required = {'status'}
        else:
            return attrs
        
        sent = set(initial)
        errors = {}

        for field in sent - allowed:
            errors.setdefault(field, []).append("This field is not allowed.")

        for field in required - sent:
            errors.setdefault(field, []).append("This field is required.")

        status_values = initial.get('status')

        if status_values is not None:
            valid_statuses = [choice[0] for choice in Order.status_choices]

            if status_values not in valid_statuses:
                errors.setdefault('status', []).append(
                    f"Invalid status '{status_values}'. Valid statuses are: {', '.join(valid_statuses)}."
                )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

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

     