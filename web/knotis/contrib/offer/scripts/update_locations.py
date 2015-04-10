
from knotis.contrib.offer.models import (
    Offer,
    LocationItem
)


def set_offer_locations(offer_type=None):
    if offer_type is not None:
        all_offers = Offer.objects.filter(offer_type=offer_type)
    else:
        all_offers = Offer.objects.all()

    broken_offers = filter(lambda x: x.get_location() is None, all_offers)

    fixable_offers = [
        (
            x,
            LocationItem.objects.filter(
                related_object_id=x.owner.pk
            )[0].location
        ) for x in broken_offers if len(
            LocationItem.objects.filter(related_object_id=x.owner.pk)
        ) != 0
    ]

    for offer, location in fixable_offers:
        LocationItem.objects.create(
            location=location,
            related_object_id=offer.pk
        )
