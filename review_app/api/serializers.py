from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.reverse import reverse

from review_app.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for review model.

    Validates rating range (1-5) and business user type.
    Prevents duplicate reviews from the same reviewer to business user.
    Restricts update fields to rating and description only.
    """

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

    def validate_rating(self, value):
        """
        Validate that rating is between 1 and 5.

        Args:
            value: Rating value to validate

        Returns:
            int: Validated rating value

        Raises:
            ValidationError: If rating is not between 1 and 5
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

    def _check_duplicate_review(self, request, business_user):
        """
        Check for duplicate review.

        Args:
            request: HTTP request object
            business_user: Business user being reviewed

        Raises:
            ValidationError: If duplicate review exists
        """
        if business_user and Review.objects.filter(
            reviewer=request.user,
            business_user=business_user
        ).exists():
            raise serializers.ValidationError(
                'You have already reviewed this business user.'
            )

    def _check_update_fields(self, sent_fields):
        """
        Check update field restrictions.

        Args:
            sent_fields: Set of fields sent in request

        Raises:
            ValidationError: If disallowed fields present
        """
        allowed = {'rating', 'description'}
        disallowed = sent_fields - allowed
        if disallowed:
            raise serializers.ValidationError(
                f'You can only update the following fields: {", ".join(allowed)}. '
            )

    def validate(self, attrs):
        """
        Validate review data based on action type.

        Args:
            attrs: Dictionary of validated attributes

        Returns:
            dict: Validated attributes

        Raises:
            ValidationError: If validation errors occur
        """
        request = self.context.get('request')
        view = self.context.get('view')
        action = getattr(view, 'action', None) if view else None

        if request and request.method == 'POST' and action == 'create':
            self._check_duplicate_review(request, attrs.get('business_user'))

        if request and request.method in ['PUT', 'PATCH'] and action in ['update', 'partial_update']:
            self._check_update_fields(set(getattr(self, 'initial_data', {}).keys()))

        return attrs