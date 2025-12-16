from rest_framework.reverse import reverse
from rest_framework import serializers
from review_app.models import Review
from django.contrib.auth.models import User

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(profile__type='business'), error_messages={
            'does_not_exist': 'Business user with the given ID does not exist.'})

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewer']

    def validate(self, attrs):
        request = self.context.get('request')
        view = self.context.get('view')
        action = getattr(view, 'action', None) if view else None

        if request and request.method in [ 'PUT', 'PATCH'] and action in ['update', 'partial_update']:
            allowed = {'rating', 'description'}
            sent = set(getattr(self, 'initial_data', {}).keys())
            disallowed = sent - allowed

            if disallowed:
                raise serializers.ValidationError(
                    f'You can only update the following fields: {", ".join(allowed)}. '
                )
        return attrs