from rest_framework.reverse import reverse
from rest_framework import serializers
from offer_app.models import Offer, OfferDetail
from django.contrib.auth.models import User


class OfferDetailSerializer(serializers.ModelSerializer):

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
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            for detail_data in details_data:

                offer_type = detail_data.get('offer_type')

                if offer_type is None:
                    raise serializers.ValidationError(
                        {"error": "offer_type is required to update OfferDetail."})
                try:
                    detail_instance = OfferDetail.objects.get(
                        offer=instance, offer_type=offer_type)
                except OfferDetail.DoesNotExist:
                    raise serializers.ValidationError(
                        {"error": f"No OfferDetail with offer_type '{offer_type}' exists for this offer."})

                detail_data = detail_data.copy()
                detail_data.pop('id', None)
                detail_data.pop('offer_type', None)

                for attr, value in detail_data.items():
                    setattr(detail_instance, attr, value)
                detail_instance.save()

        return instance

    def get_user_details(self, obj):
        user = obj.user
        return {
            'first_name': user.profile.first_name,
            'last_name': user.profile.last_name,
            'username': user.username,
        }

    def to_representation(self, instance):
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
                    'url': reverse('offers-detail', args=[details.id], request=request),
                }
                for details in instance.details.all()
            ]

            return data

        data.pop('min_price', None)
        data.pop('min_delivery_time', None)
        data.pop('user_details', None)

        return data
