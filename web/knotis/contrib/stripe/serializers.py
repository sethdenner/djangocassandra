from rest_framework.serializers import (
    Serializer,
    CharField,
    IntegerField,
    BooleanField,
    EmailField
)


class StripeCustomerSerializer(Serializer):
    pk = CharField(source='id')
    livemode = BooleanField()
    created = IntegerField()
    account_balance = IntegerField()
    currency = CharField()
    description = CharField()
    email = EmailField()
