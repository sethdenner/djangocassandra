from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.transaction.models import (
    TransactionCollection
)
from knotis.contrib.promocode.models import (
    PromoCodeTypes
)

from functools import partial


class PromoCodeTypeNotFound(Exception):
    pass


class AlreadyUsedException(Exception):
    pass


class PromoCodeApi(object):
    @staticmethod
    def execute_promo_code(
        request=None,
        current_identity=None,
        promo_code=None,
    ):
        if promo_code.promo_code_type == PromoCodeTypes.OFFER_COLLECTION:

            return PromoCodeApi.connect_offer_collection(
                request,
                current_identity,
                promo_code
            )

        elif promo_code.promo_code_type ==\
                PromoCodeTypes.RANDOM_OFFER_COLLECTION:
            return '/qrcode/random/%s/' % promo_code.context, None

        else:
            raise PromoCodeTypeNotFound

    @staticmethod
    def connect_offer_collection(
        request=None,
        current_identity=None,
        promo_code=None,
    ):
        transaction_collection = TransactionCollection.objects.get(
            pk=promo_code.context
        )
        if current_identity is None:
            url = '/qrcode/connect/%s/' % transaction_collection.pk
            return url, None

        exec_func = partial(
            TransactionApi.transfer_transaction_collection,
            request,
            current_identity,
            transaction_collection,
        )

        url = '/qrcode/connect/%s/' % transaction_collection.pk

        return url, exec_func
