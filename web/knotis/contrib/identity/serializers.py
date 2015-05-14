from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    URLField,
    UUIDField,
)

from knotis.contrib.stripe.api import StripeApi
from knotis.contrib.transaction.api import PurchaseMode
from knotis.contrib.media.serializers import CroppedImageUrlSerializer

from knotis.contrib.location.models import LocationItem

from .models import Identity


class IdentitySwitcherSerializer(ModelSerializer):
    class Meta:
        model = Identity
        fields = (
            'id',
            'badge_image',
            'name',
            'identity_type'
        )

    badge_image = CroppedImageUrlSerializer(
        read_only=True
    )
    id = UUIDField()


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
            'payment_mode',
            'available_identities',
            'badge_image',
            'banner_image',
            'tile_image_large',
            'tile_image_small',
            'location'
        )
    id = UUIDField()
    payment_mode = SerializerMethodField()
    available_identities = SerializerMethodField()
    badge_image = CroppedImageUrlSerializer(
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
    location = SerializerMethodField()

    def get_payment_mode(
        self,
        obj
    ):
        try:
            stripe_customer = StripeApi.get_customer(obj)

        except:
            stripe_customer = None

        return PurchaseMode.STRIPE if stripe_customer else PurchaseMode.NONE

    def get_available_identities(
        self,
        obj
    ):
        request = self.context.get('request')
        if request and request.user:
            try:
                available = Identity.objects.get_available(request.user)
                return [a.pk for a in available]

            except:
                pass

        return []

    def get_location(
        self,
        obj
    ):
        try:
            location_item = LocationItem.objects.get(related_object_id=obj.pk)
            address = location_item.location.address

        except:
            address = None

        return address


class IndividualSerializer(IdentitySerializer):
    class Meta:
        model = Identity
        fields = (
            'id',
            'name',
            'backend_name',
            'description',
            'badge_image',
            'banner_image',
            'tile_image_large',
            'tile_image_small'
        )


class EstablishmentSerializer(IdentitySerializer):
    class Meta:
        model = Identity
        fields = (
            'id',
            'name',
            'backend_name',
            'description',
            'badge_image',
            'banner_image',
            'tile_image_large',
            'tile_image_small',
            'location'
        )


class BusinessSerializer(IdentitySerializer):
    class Meta:
        model = Identity
        fields = (
            'id',
            'name',
            'backend_name',
            'description',
            'badge_image',
            'banner_image',
            'tile_image_large',
            'tile_image_small',
            'location'
        )
