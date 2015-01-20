from knotis.contrib.offer.tests.utils import OfferTestUtils
from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from knotis.contrib.offer.models import OfferCollection
from knotis.contrib.transaction.api import TransactionApi
import random


class TransactionTestUtils(object):
    @staticmethod
    def create_test_transaction_collection(
        **kwargs
    ):

        if kwargs.get('neighborhood'):
            offer_collection = OfferCollection.objects.filter(
                neighborhood=kwargs.get('neighborhood')
            )
        else:
            offer_collection = \
                OfferTestUtils.create_test_offer_collection(numb_offers=3)

        neighborhood = offer_collection.neighborhood

        if not kwargs.get('provision_user'):
            _, provision_user = UserCreationTestUtils.create_test_user()

        if not kwargs.get('numb_books'):
            kwargs['numb_books'] = random.randint(3, 10)

        for _ in xrange(kwargs['numb_books']):
            for (
                transaction_collection,
                _,
                _,
                _
            ) in TransactionApi.create_transaction_collection(
                neighborhood,
                provision_user
            ):
                pass

        return transaction_collection
