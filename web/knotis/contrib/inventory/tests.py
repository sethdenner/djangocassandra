from django.test import TestCase

from knotis.contrib.auth.tests import UserCreationTests
from knotis.contrib.product.tests import ProductTests
from knotis.contrib.identity.tests import IdentityTests

from models import Inventory


class InventoryTests(TestCase):
    @staticmethod
    def create_test_inventory(**kwargs):
        if not kwargs.get('product'):
            kwargs['product'] = ProductTests.create_test_product()

        if not kwargs.get('provider'):
            kwargs['provider'] = IdentityTests.create_test_establishment()

        if not kwargs.get('recipient'):
            kwargs['recipient'] = kwargs['provider']

        if not kwargs.get('stock'):
            kwargs['stock'] = 10

        if not kwargs.get('retail_price'):
            kwargs['retail_price'] = 10.

        return Inventory.objects.create(**kwargs)

    def setUp(self):
        (
            self.consumer,
            self.consumer_identity
        ) = UserCreationTests.create_test_user(
            last_name='Consumer'
        )

        (
            self.merchant,
            self.merchant_identity
        ) = UserCreationTests.create_test_user(
            last_name='Merchant'
        )

        self.business = IdentityTests.create_test_business(
            owner=self.merchant_identity
        )

        self.establishment = IdentityTests.create_test_establishment(
            owner=self.business
        )

    def test_create(self):
        inventory = InventoryTests.create_test_inventory()
        self.assertIsNotNone(inventory)

    def test_split(self):
        inventory = InventoryTests.create_test_inventory(
            provider=self.establishment,
            stock=10
        )
        inventory, split = Inventory.objects.split(
            inventory,
            self.consumer_identity,
            quantity=5
        )

        self.assertEqual(inventory.stock, 5)
        self.assertEqual(split.stock, 5)

    def test_stack(self):
        inventory = InventoryTests.create_test_inventory(
            provider=self.consumer_identity,
            stock=10
        )

        incoming = InventoryTests.create_test_inventory(
            product=inventory.product,
            provider=self.establishment,
            recipient=self.consumer_identity,
            stock=5
        )

        inventory = Inventory.objects.stack(
            incoming,
            inventory
        )

        self.assertEqual(inventory.stock, 15)
        self.assertTrue(incoming.deleted)
