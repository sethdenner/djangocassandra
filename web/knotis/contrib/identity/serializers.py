from rest_framework.serializers import ModelSerializer

from .models import Identity


class IdentitySerializer(ModelSerializer):
    class Meta:
        model = Identity
        fields = (
            'id',
            'identity_type',
            'name',
            'backend_name',
            'description',
            'available',
        )
