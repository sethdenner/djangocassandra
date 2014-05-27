from rest_framework.serializers import (
    ModelSerializer,
    URLField,
    FloatField
)

from knotis.contrib.identity.serializers import IdentitySerializer
from knotis.contrib.media.serializers import (
    CroppedImageUrlSerializer
)

from .models import (
    Offer,
    OfferAvailability
)


class OfferSerializer(ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'id',
            'owner',
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
            'last_purchase',
            'price'
        )

    owner = IdentitySerializer()
    price = FloatField(
        source='price_discount',
        read_only=True
    )
    banner_url = URLField(
        source='banner_url',
        read_only=True
    )
    badge_url = URLField(
        source='badge_url',
        read_only=True
    )


class OfferAvailabilitySerializer(ModelSerializer):
    class Meta:
        model = OfferAvailability
        fields = (
            'id',
            'title',
            'stock',
            'purchased',
            'banner_image',
            'badge_image',
            'price'
        )

    banner_image = CroppedImageUrlSerializer(
        source='default_image',
        read_only=True
    )
    badge_image = CroppedImageUrlSerializer(
        source='profile_badge',
        read_only=True
    )
