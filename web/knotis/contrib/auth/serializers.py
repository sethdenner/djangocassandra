from rest_framework.fields import (
    CharField,
    IntegerField
)

from rest_framework.serializers import ModelSerializer

from .models import (
    KnotisUser,
    UserInformation
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = KnotisUser


class UserInformationSerializer(ModelSerializer):
    class Meta:
        model = UserInformation
        exclude = (
            '_denormalized_auth_KnotisUser_username',
            'content_type',
            'deleted',
            'pub_date',
            '_denormalized_auth_KnotisUser_username_pk'
        )

    username = CharField(source='_denormalized_auth_KnotisUser_username')
    default_identity_type = IntegerField(
        source='default_identity.identity_type'
    )
