from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.reverse import reverse

from offer_app.models import OfferDetail
from order_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for order model.

    Handles order creation and status updates with field validation.
    Includes nested offer detail information in read operations.
    Validates allowed fields based on request method and action.
    """

    offer_detail_id = serializers.IntegerField(source='offer_detail.id', required=False)

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

    def _get_allowed_fields(self, method, action):
        """
        Get allowed fields for action.

        Args:
            method: HTTP method
            action: ViewSet action name

        Returns:
            tuple: (allowed_fields, required_fields) or (None, None)
        """
        if method == 'POST' and action == 'create':
            return {'offer_detail_id'}, {'offer_detail_id'}
        elif method == 'PATCH' and action == 'partial_update':
            return {'status'}, {'status'}
        return None, None

    def _validate_fields(self, allowed, required, sent, errors):
        """
        Validate field presence.

        Args:
            allowed: Set of allowed field names
            required: Set of required field names
            sent: Set of sent field names
            errors: Error dictionary to populate
        """
        for field in sent - allowed:
            errors.setdefault(field, []).append("This field is not allowed.")
        for field in required - sent:
            errors.setdefault(field, []).append("This field is required.")

    def _validate_status(self, status_value, errors):
        """
        Validate status value.

        Args:
            status_value: Status value to validate
            errors: Error dictionary to populate
        """
        if status_value is not None:
            valid_statuses = [choice[0] for choice in Order.status_choices]
            if status_value not in valid_statuses:
                errors.setdefault('status', []).append(
                    f"Invalid status '{status_value}'. Valid statuses are: {', '.join(valid_statuses)}."
                )

    def validate(self, attrs):
        """
        Validate order data based on action type.

        Args:
            attrs: Dictionary of validated attributes

        Returns:
            dict: Validated attributes

        Raises:
            ValidationError: If validation errors occur
        """
        attrs = super().validate(attrs)
        request = self.context.get('request')
        view = self.context.get('view')
        method = getattr(request, 'method', None)
        action = getattr(view, 'action', None)
        initial = self.initial_data or {}

        allowed, required = self._get_allowed_fields(method, action)
        if not allowed:
            return attrs

        errors = {}
        self._validate_fields(allowed, required, set(initial), errors)
        self._validate_status(initial.get('status'), errors)

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        """
        Create a new order.

        Retrieves offer detail, sets business and customer users,
        and creates the order instance.

        Args:
            validated_data: Dictionary of validated order data

        Returns:
            Order: Created order instance

        Raises:
            NotFound: If offer detail doesn't exist
        """
        request = self.context.get('request')
        offer_detail_id = self.initial_data.get('offer_detail_id')
        
        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise NotFound(detail="Offer detail with the given ID does not exist.")
        
        validated_data['offer_detail'] = offer_detail
        validated_data['business_user'] = offer_detail.offer.user
        validated_data['customer_user'] = request.user
        order = Order.objects.create(**validated_data)
        return order

    def to_representation(self, instance):
        """
        Convert order to dictionary representation.

        Customizes output based on request method and action.
        Removes offer_detail_id from response.
        For create action: also removes updated_at.

        Args:
            instance: Order instance to serialize

        Returns:
            dict: Serialized order data
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')

        action = getattr(view, 'action', None) if view else None
        data.pop('offer_detail_id', None)

        if request and request.method == 'POST' and action == 'create':
            data.pop('updated_at', None)

            return data

        return data

     