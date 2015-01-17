
from unittest import TestCase

from .utils import OfferTestUtils
from knotis.contrib.offer.models import (
    Offer,
    OfferTypes,
    OfferCollectionItem,
)


class DarkOfferTests(TestCase):
    def setUp(self):
        self.offer = OfferTestUtils.create_test_offer(
            title='Foobar',
            offer_type=OfferTypes.DARK
        )

    def test_title(self):
        self.assertEqual(
            self.offer.title,
            'Foobar'
        )


class NormalOfferTests(TestCase):
    def setUp(self):
        self.offer = OfferTestUtils.create_test_offer(
            title='Foobar',
            offer_type=OfferTypes.NORMAL
        )

    def test_create_dark(self):
        offer = Offer.objects.get(pk=self.offer.id)
        self.assertEqual(
            offer.title,
            'Foobar'
        )


class OfferCollectionTests(TestCase):
    def setUp(self):
        self.offer_collection = OfferTestUtils.create_test_offer_collection(
            title='Foobar',
            numb_offers=3
        )

    def test_offer_type(self):
        offer = Offer.objects.get(description=self.offer_collection.pk)
        self.assertEqual(
            offer.offer_type,
            OfferTypes.DIGITAL_OFFER_COLLECTION
        )

    def test_offer_published(self):
        offer = Offer.objects.get(description=self.offer_collection.id)
        self.assertTrue(offer.active)
        self.assertTrue(offer.published)

    def test_offer_collection(self):
        offer_collection_items = OfferCollectionItem.objects.filter(
            offer_collection=self.offer_collection
        )
        self.assertEqual(len(offer_collection_items), 3)
