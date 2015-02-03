
from unittest import TestCase

from .utils import OfferTestUtils
from knotis.contrib.identity.tests.utils import IdentityModelTestUtils
from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from knotis.contrib.offer.api import (
    OfferApi
)

from knotis.contrib.transaction.api import (
    TransactionApi
)

from knotis.contrib.offer.models import (
    Offer,
    OfferTypes,
    OfferCollectionItem,
    OfferCollection,
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


class RandomOfferTests(TestCase):
    def setUp(self):

        owner = IdentityModelTestUtils.create_test_establishment()
        offer_collection_1 = OfferTestUtils.create_test_offer_collection(
            title='Foobar',
            owner=owner,
            numb_offers=3
        )
        offer_collection_2 = OfferTestUtils.create_test_offer_collection(
            title='baz',
            owner=owner,
            numb_offers=3
        )
        self.random_offer = OfferApi.create_random_offer_collection(
            [offer_collection_1, offer_collection_2],
            owner=owner
        )

    def test_offer_count(self):
        offer_collection = OfferCollection.objects.get(
            pk=self.random_offer.description
        )
        offer_collection_items = OfferCollectionItem.objects.filter(
            offer_collection=offer_collection
        )
        self.assertEqual(len(offer_collection_items), 6)

    def test_random_offer_connect(self):
        user, identity = UserCreationTestUtils.create_test_user()

        samples = 3

        connect_transactions = TransactionApi.purchase_random_collection(
            None,
            self.random_offer.id,
            identity,
            sample_size=samples
        )
        self.assertEqual(len(connect_transactions), (1 + samples)*2)
