from rest_framework import serializers
from rest_framework.reverse import reverse

from offer_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for offer detail model.

    Represents a specific tier (basic, standard, premium) of an offer
    with pricing, delivery time, and features.
    """
    features = serializers.ListField(child=serializers.CharField())


    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type'
        ]


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for offer model.

    Handles nested offer details creation and updates.
    Validates that offers include all three types (basic, standard, premium).
    Provides different representations for list and detail views.
    """

    details = OfferDetailSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    user_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details'
        ]
        read_only_fields = ['id', 'created_at',
                            'updated_at', 'min_delivery_time', 'user_details']

    def validate_details(self, value):
        """
        Validate that offer details include all required types.

        Args:
            value: List of offer detail dictionaries

        Returns:
            list: Validated offer details

        Raises:
            ValidationError: If not exactly 3 details or missing required types
        """
        if self.instance is None:
            if len(value) != 3:
                raise serializers.ValidationError(
                    {"error": "Exactly three offer details (basic, standard, premium) are required."})
            offer_types = {detail['offer_type'] for detail in value}
            if len(set(offer_types)) != 3:
                raise serializers.ValidationError(
                    {"error": "Offer details must include exactly one of each type: basic, standard, premium."})
        return value

    def create(self, validated_data):
        """
        Create offer with nested offer details.

        Args:
            validated_data: Dictionary of validated offer and details data

        Returns:
            Offer: Created offer instance with associated details
        """
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def _update_offer_detail(self, instance, detail_data):
        """
        Update a single offer detail.

        Args:
            instance: Offer instance
            detail_data: Dictionary with detail update data

        Returns:
            OfferDetail: The detail instance to update

        Raises:
            ValidationError: If offer_type missing or detail not found
        """
        offer_type = detail_data.get('offer_type')
        if offer_type is None:
            raise serializers.ValidationError(
                {"error": "offer_type is required to update OfferDetail."})
        
        try:
            return OfferDetail.objects.get(offer=instance, offer_type=offer_type)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError(
                {"error": f"No OfferDetail with offer_type '{offer_type}' exists for this offer."})

    def _apply_detail_updates(self, detail_instance, detail_data):
        """
        Apply updates to detail instance.

        Args:
            detail_instance: OfferDetail instance to update
            detail_data: Dictionary with field updates
        """
        detail_data = detail_data.copy()
        detail_data.pop('id', None)
        detail_data.pop('offer_type', None)
        for attr, value in detail_data.items():
            setattr(detail_instance, attr, value)
        detail_instance.save()

    def update(self, instance, validated_data):
        """
        Update offer and its nested offer details.

        Args:
            instance: Offer instance to update
            validated_data: Dictionary of validated offer and details data

        Returns:
            Offer: Updated offer instance
        """
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data:
            for detail_data in details_data:
                detail_instance = self._update_offer_detail(instance, detail_data)
                self._apply_detail_updates(detail_instance, detail_data)

        return instance

    def get_user_details(self, obj):
        """
        Get user details from offer creator.

        Args:
            obj: Offer instance

        Returns:
            dict: Dictionary containing user's first name, last name, and username
        """
        user = obj.user
        return {
            'first_name': user.profile.first_name,
            'last_name': user.profile.last_name,
            'username': user.username,
        }

    def to_representation(self, instance):
        """
        Convert offer to dictionary representation.

        Customizes output based on request method and action.
        For list view: shows minimal detail information.
        For retrieve view: shows detail URLs.
        For create/update: shows full nested details.

        Args:
            instance: Offer instance to serialize

        Returns:
            dict: Serialized offer data
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')

        action = getattr(view, 'action', None) if view else None

        if request and request.method == 'GET' and action == 'list':
            data['details'] = [
                {
                    'id': details.id,
                    'url': f"/offerdetails/{details.id}/",
                }
                for details in instance.details.all()
            ]
            return data

        if request and request.method == 'GET' and action == 'retrieve':
            data.pop('user_details', None)
            data['details'] = [
                {
                    'id': details.id,
                    'url': reverse('offer-details', args=[details.id], request=request),
                }
                for details in instance.details.all()
            ]

            return data

        data.pop('min_price', None)
        data.pop('min_delivery_time', None)
        data.pop('user_details', None)

        return data
