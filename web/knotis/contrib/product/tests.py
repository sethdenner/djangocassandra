from django.test import TestCase

from models import (
    Product,
    ProductTypes
)


class ProductTests(TestCase):
    @staticmethod
    def create_test_product(**kwargs):
        if not kwargs.get('product_type'):
            kwargs['product_type'] = ProductTypes.PHYSICAL

        if not kwargs.get('title'):
            kwargs['title'] = 'Test Product'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test product description.'

        if not kwargs.get('sku'):
            kwargs['sku'] = '0000000000000000'

        return Product.objects.create(**kwargs)

    def test_create(self):
        product = ProductTests.create_test_product()
        self.assertIsNotNone(product)
