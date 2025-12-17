from collections import OrderedDict

from rest_framework import serializers

from ..models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for complete user profile data.

    Includes all profile fields and email from related User model.
    Handles email updates through the User model.
    Converts null values to empty strings for better frontend handling.
    """

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(
        source='user.username', read_only=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                  'tel', 'description',  'working_hours', 'type', 'email', 'created_at', ]
        read_only_fields = ['created_at', 'type', 'user', 'username']

    def to_representation(self, instance):
        """
        Convert Profile instance to dictionary representation.

        Replaces None values with empty strings and includes user email.
        Returns fields in a specific order.

        Args:
            instance: Profile instance to serialize

        Returns:
            OrderedDict: Serialized profile data with ordered fields
        """
        data = super().to_representation(instance)

        for field in [
                'first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            if field in data and data[field] is None:
                data[field] = ''

        data['email'] = instance.user.email or ""
        field_order = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                       'tel', 'description',  'working_hours', 'type', 'email', 'created_at', ]

        ordered = OrderedDict()
        for field in field_order:
            if field in data:
                ordered[field] = data[field]

        return ordered

    def update(self, instance, validated_data):
        """
        Update profile instance and optionally user email.

        Args:
            instance: Profile instance to update
            validated_data: Dictionary of validated field values

        Returns:
            Profile: Updated profile instance
        """
        email = validated_data.pop('email', None)

        if email is not None:
            user = instance.user
            user.email = email
            user.save(update_fields=['email'])

        return super().update(instance, validated_data)


class ProfileBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for user profile data.

    Includes essential profile information without email field.
    Used for listing profiles with reduced data exposure.
    """

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(
        source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                  'tel', 'description',  'working_hours', 'type', ]
        read_only_fields = ['created_at', 'type', 'user', 'username']


    def to_representation(self, instance):
        """
        Convert Profile instance to dictionary representation.

        Replaces None values with empty strings.
        Returns fields in a specific order without email.

        Args:
            instance: Profile instance to serialize

        Returns:
            OrderedDict: Serialized profile data with ordered fields
        """
        data = super().to_representation(instance)

        for field in [
                'first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            if field in data and data[field] is None:
                data[field] = ''

        field_order = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                       'tel', 'description',  'working_hours', 'type', ]

        ordered = OrderedDict()
        for field in field_order:
            if field in data:
                ordered[field] = data[field]

        return ordered


class ProfileBusinessSerializer(ProfileBasicSerializer):
    """
    Serializer for business user profiles.

    Extends ProfileBasicSerializer with business-specific fields.
    Includes working hours and description fields.
    """

    class Meta(ProfileBasicSerializer.Meta):
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                  'tel', 'description',  'working_hours', 'type']


class ProfileCustomerSerializer(ProfileBasicSerializer):
    """
    Serializer for customer user profiles.

    Extends ProfileBasicSerializer with minimal customer fields.
    Excludes detailed business information.
    """

    class Meta(ProfileBasicSerializer.Meta):
        model = Profile
        fields = ['user', 'username', 'first_name',
                  'last_name', 'file', 'type']
