import datetime

from django.test import TestCase

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)
from knotis.contrib.offer.models import (
    Offer,
    OfferTitleTypes
)
from knotis.contrib.product.models import Product
from knotis.contrib.inventory.models import Inventory

from models import Transaction


class TransactionTests(TestCase):
    def setUp(self):
        self.consumer, self.consumer_identity = KnotisUser.objects.create_user(
            'Test',
            'Consumer',
            'test_consumer@example.com',
            'test_password'
        )

        self.merchant, self.merchant_identity = KnotisUser.objects.create_user(
            'Test',
            'Merchant',
            'test_merchant@example.com',
            'test_password'
        )

        self.business = Identity.objects.create(
            owner=self.merchant_identity,
            identity_type=IdentityTypes.BUSINESS,
            name='Test Business',
            description='Test business description.'
        )

        self.establishment = Identity.objects.create(
            owner=self.business,
            identity_type=IdentityTypes.ESTABLISHMENT,
            name='Test Establishment',
            description='Test Business\'s primary location.'
        )

        self.product = Product.objects.create(
            title='Test Product',
            description='Test product description.',
            public=True,
            sku='00000000000'
        )

        self.establishment_inventory = Inventory.objects.create(
            product=self.product,
            owner=self.establishment,
            supplier=self.establishment,
            stock=10,
            retail_price=10.
        )

        self.establishment_offer = Offer.objects.create_offer(
            self.establishment,
            'Test Offer',
            OfferTitleTypes.TITLE_1,
            'Test offer description.',
            'Test offer restrictions.',
            None,
            None,
            None,
            None,
            10.,
            1.,
            None,
            datetime.datetime.utcnow(),
            datetime.datetime.utcnow() + datetime.timedelta(days=1),
            10,
            False,
            True,
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
