from unittest import TestCase

from knotis.contrib.offer.tests.utils import OfferTestUtils
from knotis.contrib.auth.tests.utils import UserCreationTestUtils

from knotis.contrib.transaction.api import (
    PurchaseMode,
    TransactionApi,
)
from knotis.contrib.offer.models import Offer
from knotis.contrib.product.models import (
    Product,
    CurrencyCodes
)
from knotis.contrib.inventory.models import Inventory
from .utils import TransactionTestUtils


class TestBookProvision(TestCase):
    def setUp(self):
        self.transaction_collection = \
            TransactionTestUtils.create_test_transaction_collection()

    def test_is_not_none(self):
        self.assertIsNotNone(self.transaction_collection)


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
            stock=1,
            get_existing=True
        )

    def test_purchase(self):

        TransactionApi.create_purchase(
            request=None,
            offer=self.offer,
            buyer=self.buyer,
            currency=self.buyer_usd,
            mode=PurchaseMode.STRIPE
        )
