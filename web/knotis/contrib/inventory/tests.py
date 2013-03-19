from django.test import TestCase

from knotis.contrib.product.tests import ProductTests
from knotis.contrib.product.tests import IdentityTests

from models import Inventory


class InventoryTests(TestCase):
    @staticmethod
    def create_test_inventory(**kwargs):
        if not kwargs.get('product'):
            kwargs['product'] = ProductTests.create_test_product()

        if not kwargs.get('owner'):
            kwargs['owner'] = IdentityTests.create_test_establishement()

        if not kwargs.get('supplier'):
            kwargs['supplier'] = kwargs['owner']

        if not kwargs.get('stock'):
            kwargs['stock'] = 10

        if not kwargs.get('retail_price'):
            kwargs['retail_price'] = 10.

        return Inventory.objects.create(**kwargs)

    def test_create(self):
        inventory = InventoryTests.create_test_inventory()
        self.assertIsNotNone(inventory)
