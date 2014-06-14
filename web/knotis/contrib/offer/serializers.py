from rest_framework.serializers import (
    ModelSerializer,
    FloatField,
    CharField
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
            'price',
            'banner_image',
            'badge_image'
        )

    owner = IdentitySerializer()
    price = FloatField(
        source='price_discount',
        read_only=True
    )
    banner_image = CroppedImageUrlSerializer(
        source='banner_image',
        read_only=True
    )
    badge_image = CroppedImageUrlSerializer(
        source='badge_image',
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
            'price',
            'business_name'
        )

    banner_image = CroppedImageUrlSerializer(
        source='default_image',
        read_only=True
    )
    badge_image = CroppedImageUrlSerializer(
        source='profile_badge',
        read_only=True
    )
    business_name = CharField(
        read_only=True,
        source='identity.name'
    )
