
from knotis.contrib.media.models import ImageInstance

from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager,
)

from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickIPAddressField,
    QuickForeignKey,
    QuickGenericForeignKey,
    QuickIntegerField,
)

from knotis.contrib.offer.models import Offer, OfferItem

from django.db.models.signals import post_save
from django.dispatch import receiver

#from knotis.contrib.activity.models import ActivityTypes
from knotis.contrib.product.models import CurrencyCodes

class Reward(QuickModel):
    pass


class RewardOfferManager(QuickManager):
    pass


class RewardOffer(QuickModel):

    @staticmethod
    @receiver(post_save, sender=Offer)
    def offer_handler(**kwargs):
        offer = kwargs['instance']
        offer_items = OfferItem.objects.filter(offer=offer)
        for i in offer_items:
            if i.inventory.product.currency == CurrencyCodes.KNOTIS_POINTS:
                RewardOffer.objects.create(**kwargs)

    offer = QuickForeignKey(Offer)
    objects = RewardOfferManager()
    default_image = QuickForeignKey(ImageInstance)
    title = QuickCharField(max_length=140)
