from rest_framework.serializers import (
    ModelSerializer,
    CharField
)

from knotis.contrib.media.serializers import CroppedImageUrlSerializer

from .models import Transaction


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id',
            'owner',
            'transaction_type',
            'offer',
            'transaction_context',
            'reverted',
            'offer_badge_image',
            'offer_banner_image',
            'offer_title'
        )

    offer_badge_image = CroppedImageUrlSerializer(
        source='offer.badge_image',
        read_only=True
    )
    offer_banner_image = CroppedImageUrlSerializer(
        source='offer.banner_image',
        read_only=True
    )
    offer_title = CharField(
        source='offer.title',
        read_only=True
    )
