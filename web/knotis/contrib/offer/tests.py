import datetime

from django.test import TestCase

from knotis.contrib.identity.tests import IdentityTests
from knotis.contrib.media.tests import MediaTests

from knotis.contrib.product.models import (
    Product
)

from knotis.contrib.offer.models import (
    Offer,
    OfferTypes,
    OfferStatus,
    OfferTitleTypes
)


class OfferTests(TestCase):
    @staticmethod
    def create_test_offer(
        **kwargs
    ):
        if not kwargs.get('owner'):
            kwargs['owner'] = IdentityTests.create_test_establishment()

        if not kwargs.get('offer_type'):
            kwargs['offer_type'] = OfferTypes.NORMAL

        if not kwargs.get('title'):
            kwargs['title'] = 'Test offer title'

        if not kwargs.get('title_type'):
            kwargs['title_type'] = OfferTitleTypes.TITLE_1

        if not kwargs.get('description'):
            kwargs['description'] = 'Test offer description'

        if not kwargs.get('default_image'):
            kwargs['default_image'] = MediaTests.create_test_image(
                owner=kwargs['owner']
            )

        if not kwargs.get('price_retail'):
            kwargs['price_retail'] = 10.

        if not kwargs.get('price_discount'):
            kwargs['price_discount'] = kwargs['price_retail'] * .5

        if not kwargs.get('currency'):
            kwargs['currency'] = Product.currency.get('usd')

        if not kwargs.get('status'):
            kwargs['status'] = OfferStatus.CURRENT

        if not kwargs.get('published'):
            kwargs['published'] = True

        if not kwargs.get('active'):
            kwargs['active'] = True

        if not kwargs.get('restrictions'):
            kwargs['restrictions'] = 'Test offer restrictions'

        if not kwargs.get('stock'):
            kwargs['stock'] = 10

        if not kwargs.get('start_date'):
            kwargs['start_date'] = datetime.datetime.utcnow()

        if not kwargs.get('end_date'):
            kwargs['end_date'] = kwargs['start_date'] + datetime.timedelta(
                days=7
            )

        offer = Offer.objects.create(**kwargs)

        offer.default_image.related_object_id = offer.id
        offer.default_image.save()

        return offer

    def test_create(self):
        offer = OfferTests.create_test_offer()
        self.assertIsNotNone(offer)
