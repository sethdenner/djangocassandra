
from unittest import TestCase
from django.test.client import RequestFactory
from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from knotis.contrib.promocode.tests.utils import PromoCodeTestUtils
from knotis.contrib.promocode.api import (
    PromoCodeApi,
)
from knotis.contrib.transaction.models import Transaction
from knotis.contrib.transaction.api import (
    TransactionApi
)
from knotis.contrib.activity.models import (
    Activity,
)


class ConnectPromoCodeTests(TestCase):
    def setUp(self):
        self.promo_code = \
            PromoCodeTestUtils.create_test_collection_promo_code()

        self.knotis_user, self.identity = \
            UserCreationTestUtils.create_test_user()

        self.request = RequestFactory()
        self.request.user = self.knotis_user
        self.request.raw_post_date = ''

        self.request.META = {'REMOTE_ADDR': '0.0.0.0'}

        PromoCodeApi.connect_offer_collection(
            self.request,
            self.identity,
            self.promo_code
        )

        self.activities = Activity.objects.filter(
            context=self.promo_code.value
        )

    def test_activity(self):
        self.assertGreaterEqual(self.activities, 1)

    def test_no_duplicate(self):
        self.assertRaises(
            TransactionApi.TransactionCollectionAlreadyTransfered,
            PromoCodeApi.connect_offer_collection,
            self.request, self.identity, self.promo_code
        )

    def test_transfer(self):
        my_transactions = Transaction.objects.filter(owner=self.identity)
        self.assertGreater(len(my_transactions), 1)
