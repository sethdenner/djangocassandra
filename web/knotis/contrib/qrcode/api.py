from django.utils.log import logging
logger = logging.getLogger(__name__)

from rest_framework.exceptions import APIException
from rest_framework.renderers import JSONRenderer

from knotis.views import ApiViewSet

from knotis.contrib.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.transaction.serializers import TransactionSerializer

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin


class RedemptionScanApiViewSet(ApiViewSet, GetCurrentIdentityMixin):
    api_path = 'qrcode/redeem'
    resource_name = 'redemption-scan'

    serializer_class = TransactionSerializer

    def initial(
        self,
        request,
        *args,
        **kwargs
    ):
        super(RedemptionScanApiViewSet, self).initial(
            request,
            *args,
            **kwargs
        )

        self.get_current_identity(request)

    def retrieve(
        self,
        request,
        pk=None
    ):
        if not pk:
            raise self.NoPurchasePkProvidedException()

        if not self.current_identity:
            raise self.FailedToRetrieveCurrentIdentityException()

        try:
            purchase = Transaction.objects.get(
                pk=pk,
                transaction_type=TransactionTypes.PURCHASE
            )

        except Exception, e:
            logger.exception(e.message)
            raise self.PurchaseCouldNotBeRetrievedException()

        try:
            redemptions = TransactionApi.create_redemption(
                request,
                purchase,
                self.current_identity
            )

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToCreateRedemptionException()

        my_redemption = None
        for p in redemptions:
            if p.owner.pk == self.current_identity.pk:
                my_redemption = p
                break

        serializer = self.serializer_class(my_redemption)
        return JSONRenderer().render(serializer.data)

    class NoPurchasePkProvidedException(APIException):
        status_code = '500'
        default_detail = 'Redemption scans must include a purchase id.'

    class PurchaseCouldNotBeRetrievedException(APIException):
        status_code = '500'
        default_detail = 'No purchase matched the provided id.'

    class FailedToRetrieveCurrentIdentityException(APIException):
        status_code = 500
        default_detail = 'Failed to retrieve current identity.'

    class FailedToCreateRedemptionException(APIException):
        status_code = 500
        default_detail = 'Failed to create redemption.'
