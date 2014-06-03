from rest_framework.serializers import (
    ModelSerializer
)

from .models import StripeCustomer


class StripeCustomerSerializer(ModelSerializer):
    class Meta:
        model = StripeCustomer
        exclude = (
            'content_type',
            'deleted',
        )
