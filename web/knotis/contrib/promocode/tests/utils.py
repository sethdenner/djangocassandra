

from knotis.contrib.promocode.models import (
    ConnectPromoCode,
)

from knotis.contrib.transaction.tests.utils import TransactionTestUtils


class PromoCodeTestUtils(object):
    @staticmethod
    def create_test_collection_promo_code(**kwargs):

        transaction_collection = \
            TransactionTestUtils.create_test_transaction_collection(
                numb_books=1
            )

        promo_code = ConnectPromoCode.objects.get(
            context=transaction_collection.pk
        )

        return promo_code
