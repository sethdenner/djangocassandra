import datetime

from django.test import TestCase

from knotis.contrib.auth.tests import UserCreationTests
from knotis.contrib.identity.tests import IdentityTests
from knotis.contirb.product.tests import ProductTests
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

        self.business = IdentityTests.create_test_business(
            owner=self.merchant_identity
        )

        self.establishment = IdentityTests.create_test_establishment(
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
            self.establishment,
            inventory=[self.establishment_inventory]
        )

    def test_create_purchase(self):
        transaction = Transaction.objects.create_purchase(
            owner=self.establishment,
            other=self.consumer_identity,
            offer=self.establishment_offer)
        self.assertIsNotNone(transaction)

        for key, value in transaction.__dict__.iteritems():
            print '%s=%s' % (key, value)
