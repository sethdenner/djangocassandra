from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.transaction.models import (
    TransactionCollection
)
from knotis.contrib.promocode.models import (
    PromoCodeTypes
)
from knotis.contrib.activity.models import (
    Activity,
    ActivityTypes
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

        else:
            raise PromoCodeTypeNotFound

    @staticmethod
    def connect_offer_collection(
        request=None,
        current_identity=None,
        promo_code=None,
    ):
        promo_activities = Activity.objects.filter(
            context=promo_code.value,
            identity=current_identity,
            activity_type=ActivityTypes.PROMO_CODE
        )
        if len(promo_activities) > 0:
            raise AlreadyUsedException

        transaction_collection = TransactionCollection.objects.get(
            pk=promo_code.context
        )

        exec_func = partial(
            TransactionApi.transfer_transaction_collection,
            request,
            current_identity,
            transaction_collection,
        )

        Activity.objects.create(
            identity=current_identity,
            context=promo_code.value,
            activity_type=ActivityTypes.PROMO_CODE
        )
        url = '/qrcode/connect/%s/' % transaction_collection.pk

        return url, exec_func
