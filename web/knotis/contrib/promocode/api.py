from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.transaction.models import (
    TransactionCollection
)
from knotis.contrib.activity.models import (
    Activity,
    ActivityTypes
)


class PromoCodeApi(object):
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
        return TransactionApi.transfer_transaction_collection(
            request,
            current_identity,
            transaction_collection,
        )


class AlreadyUsedException(Exception):
    pass
