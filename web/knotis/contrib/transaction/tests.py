from django.test import TestCase

from knotis.contrib.auth.tests import UserCreationTests
from knotis.contrib.identity.tests import IdentityModelTests
from knotis.contrib.product.tests import ProductTests
from knotis.contrib.inventory.tests import InventoryTests
from knotis.contrib.offer.tests import OfferTests

from models import Transaction


class TransactionTests(TestCase):
    def setUp(self):
        (
            self.consumer,
            self.consumer_identity
        ) = UserCreationTests.create_test_user(
            last_name='Consumer',
            email='test_consumer@example.com',
        )

        (
            self.merchant,
            self.merchant_identity
        ) = UserCreationTests.create_test_user(
            last_name='Merchant',
            email='test_merchant@example.com',
        )

        self.business = IdentityModelTests.create_test_business(
            owner=self.merchant_identity
        )

        self.establishment = IdentityModelTests.create_test_establishment(
            owner=self.business,
            description='Test Business\'s primary location.'
        )

        self.product = ProductTests.create_test_product()

        self.establishment_inventory = InventoryTests.create_test_inventory(
            product=self.product,
            owner=self.establishment,
            supplier=self.establishment,
        )

        self.establishment_offer = OfferTests.create_test_offer(
            owner=self.establishment,
            inventory=[self.establishment_inventory]
        )

    def test_create_purchase(self):
        (
            transaction_buyer,
            transaction_seller,
            inventory
        ) = Transaction.objects.create_purchase(
            self.establishment_offer,
            self.consumer_identity
        )

        self.assertIsNotNone(transaction_buyer)
        self.assertIsNotNone(transaction_seller)
        self.assertIsNotNone(inventory)
