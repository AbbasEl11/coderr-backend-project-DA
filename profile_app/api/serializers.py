from rest_framework import serializers
from ..models import Profile
from collections import OrderedDict


class ProfileSerializer(serializers.ModelSerializer):
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
        email = validated_data.pop('email', None)

        if email is not None:
            user = instance.user
            user.email = email
            user.save(update_fields=['email'])

        return super().update(instance, validated_data)


class ProfileBasicSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(
        source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                  'tel', 'description',  'working_hours', 'type', ]
        read_only_fields = ['created_at', 'type', 'user', 'username']

    def to_representation(self, instance):
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
    class Meta(ProfileBasicSerializer.Meta):
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location',
                  'tel', 'description',  'working_hours', 'type']


class ProfileCustomerSerializer(ProfileBasicSerializer):
    class Meta(ProfileBasicSerializer.Meta):
        model = Profile
        fields = ['user', 'username', 'first_name',
                  'last_name', 'file', 'type']
