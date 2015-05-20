from unittest import TestCase
from django.test.client import RequestFactory

from knotis.contrib.offer.tests.utils import OfferTestUtils
from knotis.contrib.auth.tests.utils import UserCreationTestUtils

from knotis.contrib.transaction.api import (
    PurchaseMode,
    TransactionApi,
)
from knotis.contrib.transaction.models import (
    TransactionCollectionItem
)
from knotis.contrib.offer.models import (
    Offer,
    OfferCollection,
    OfferCollectionItem
)
from knotis.contrib.product.models import (
    Product,
    CurrencyCodes
)
from knotis.contrib.inventory.models import Inventory
from .utils import TransactionTestUtils


class TestBookConnect(TestCase):
    def setUp(self):
        self.transaction_collection = \
            TransactionTestUtils.create_test_transaction_collection()

        user, self.identity = UserCreationTestUtils.create_test_user()

        self.request = RequestFactory()
        self.request.user = user
        self.request.raw_post_date = ''

        self.request.META = {'REMOTE_ADDR': '0.0.0.0'}

    def test_transer(self):
        transfers = TransactionApi.transfer_transaction_collection(
            self.request,
            self.identity,
            self.transaction_collection,
        )
        transaction_collection_items = (
            TransactionCollectionItem.objects.filter(
                transaction_collection=self.transaction_collection
            )
        )
        self.assertEqual(
            len(transfers),
            2*len(transaction_collection_items)
        )


class TestBookPurchase(TestCase):
    def setUp(self):
        self.offer_collection = \
            OfferTestUtils.create_test_offer_collection(numb_offers=3)

        self.offer = Offer.objects.get(description=self.offer_collection.pk)
        user, self.buyer = UserCreationTestUtils.create_test_user()

        usd = Product.currency.get(CurrencyCodes.USD)
        self.buyer_usd = Inventory.objects.create_stack_from_product(
            self.buyer,
            usd,
            stock=self.offer.price_discount(),
            get_existing=True
        )

        self.request = RequestFactory()
        self.request.user = user
        self.request.raw_post_date = ''

        self.request.META = {'REMOTE_ADDR': '0.0.0.0'}

    def test_purchase(self):

        transactions = TransactionApi.create_purchase(
            request=self.request,
            offer=self.offer,
            buyer=self.buyer,
            currency=self.buyer_usd,
            mode=PurchaseMode.STRIPE
        )
        offer_collection_items = OfferCollectionItem.objects.filter(
            offer_collection=OfferCollection.objects.get(
                pk=self.offer.description
            )
        )

        self.assertEqual(
            len(transactions),
            (offer_collection_items.count() + 1)*2
        )


class TestRedemption(TestCase):
    def setUp(self):
        self.transaction_collection = \
            TransactionTestUtils.create_test_transaction_collection()

        user, self.identity = UserCreationTestUtils.create_test_user()
