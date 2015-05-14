from rest_framework import serializers

from .models import (
    UserInformation
)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True
    )


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True
    )

    password = serializers.CharField(
        required=True
    )


class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInformation
        exclude = (
            'content_type',
            'deleted',
            'pub_date',
            'username'
        )

    username = serializers.CharField(
        source='user.username'
    )
    default_identity_type = serializers.IntegerField(
        source='default_identity.identity_type'
    )
