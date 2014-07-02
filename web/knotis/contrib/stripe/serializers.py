from rest_framework.serializers import (
    Serializer,
    CharField,
    IntegerField,
    DateTimeField,
    BooleanField,
    EmailField
)


class StripeCustomerSerializer(Serializer):
    pk = CharField(source='id')
    livemode = BooleanField()
    created = DateTimeField()
    account_balance = IntegerField()
    currency = CharField()
    description = CharField()
    email = EmailField()
