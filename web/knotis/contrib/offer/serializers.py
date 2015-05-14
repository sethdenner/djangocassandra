from rest_framework.serializers import (
    ModelSerializer,
    FloatField,
    CharField,
    URLField,
    UUIDField,
)

from knotis.contrib.identity.serializers import IdentitySerializer
from knotis.contrib.media.serializers import (
    CroppedImageUrlSerializer
)

from .models import (
    Offer,
    OfferAvailability,
    OfferCollection,
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
            'price_retail',
            'banner_image',
            'badge_image',
            'tile_image_large',
            'tile_image_small'
        )
    id = UUIDField()

    owner = IdentitySerializer()
    price = FloatField(
        source='price_discount',
        read_only=True
    )
    price_retail = FloatField(
        read_only=True
    )
    banner_image = CroppedImageUrlSerializer(
        read_only=True
    )
    tile_image_small = URLField(
        read_only=True,
        max_length=1024
    )
    tile_image_large = URLField(
        read_only=True,
        max_length=1024
    )
    badge_image = CroppedImageUrlSerializer(
        read_only=True
    )


class OfferCollectionSerializer(ModelSerializer):
    class Meta:
        model = OfferCollection
        fields = (
            'offers',
        )

    offers = OfferSerializer(
        source='get_offers',
        many=True
    )


class OfferAvailabilitySerializer(ModelSerializer):
    class Meta:
        model = OfferAvailability
        fields = (
            'id',
            'offer',
            'title',
            'stock',
            'purchased',
            'banner_image',
            'badge_image',
            'price',
            'price_retail',
            'business_name'
        )

    price_retail = FloatField(
        read_only=True,
        source='offer.price_retail'
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
