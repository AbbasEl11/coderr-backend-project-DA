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
            'min_delivery_time'
        ]
        read_only_fields = ['id', 'created_at',
                            'updated_at', 'min_delivery_time']

    def validate_details(self, value):
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.method == 'GET':

            data['details'] = [
                {
                    'id': details.id,
                    'url': f"/offerdetails/{details.id}/",
                }
                for details in instance.details.all()
            ]
        return data
