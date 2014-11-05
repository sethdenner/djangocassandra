from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.offer.models import (
    Offer,
    OfferItem
)
from knotis.contrib.identity.models import (
    Identity,
)
from knotis.contrib.inventory.models import (
    Inventory
)
from knotis.contrib.transaction.models import (
    Transaction
)


def transfer_passport_offer(offer_pk, new_owner_pk):
    """
    Disclamer:
    If you didn't write this script you probably shouldn't be using it.

    Sometimes passport books get provisioned to the wrong account.

    This script solves that problem. It should be noted that it makes the
    assumption that no one has bought or redeemed anything from the old owner.

    The assumptions this script makes are that you only have one OfferItem in
    this offer - if there's more, it'll just segfault.

    WARNING:

    If you've got two different offers of the same product, all the inventories
    from the owner of that offer will be reassigned to the new owner...

    10.31.2014 - It's currently an adhoc script that's to be used for
    transfering a passport book offer and transactions to the proper owner.
    """
    offer = Offer.objects.get(pk=offer_pk)

    new_owner = Identity.objects.get(pk=new_owner_pk)
    old_owner = offer.owner

    transactions = Transaction.objects.filter(
        owner=old_owner,
        offer=offer,
    )

    for t in transactions:
        t.owner = new_owner
        t.save()

    product = OfferItem.objects.get(offer=offer).inventory.product

    for i in Inventory.objects.filter(
        provider=old_owner,
        product=product
    ):
        i.provider = new_owner
        i.save()

    for i in Inventory.objects.filter(
        recipient=old_owner,
        product=product
    ):
        i.recipient = new_owner
        i.save()

    offer.owner = new_owner
