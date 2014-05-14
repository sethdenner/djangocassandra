from rest_framework.serializers import ModelSerializer

from knotis.contrib.identity.serializers import IdentitySerializer

from .models import Offer


class OfferSerializer(ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'id',
            'offer_type',
            'title',
            'description',
            'restrictions',
            'start_time',
            'end_time',
            'stock',
            'unlimited',
            'purchased',
            'redeemed',
            'published',
            'active',
            'completed',
            'last_purchase'
        )

    owner = IdentitySerializer()
