from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField
)
from rest_framework.pagination import PaginationSerializer

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
        source='badge_image',
        read_only=True
    )


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
            'banner_image'
        )

    payment_mode = SerializerMethodField('get_payment_mode')
    available_identities = SerializerMethodField('get_available_identities')
    badge_image = CroppedImageUrlSerializer(
        source='badge_image',
        read_only=True
    )
    banner_image = CroppedImageUrlSerializer(
        source='banner_image',
        read_only=True
    )
    location = SerializerMethodField('get_location')

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
            'banner_image'
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
            'location'
        )


class PaginatedEstablishmentSerializer(PaginationSerializer):
    class Meta:
        object_serializer_class = EstablishmentSerializer


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
            'location'
        )
