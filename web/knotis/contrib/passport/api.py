from knotis.contrib.transaction.api import TransactionApi
from rest_framework.decorators import detail_route

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.views import ApiViewSet


class PassportApiViewSet(ApiViewSet, GetCurrentIdentityMixin):
    api_path = 'passport'
    resource_name = 'passport'

    def initial(
        self,
        request,
        *args,
        **kwargs
    ):
        super(PassportApiViewSet, self).initial(
            request,
            *args,
            **kwargs
        )

        self.get_current_identity(request)

    @detail_route()
    def connect(
        self,
        request,
        pk=None
    ):
        if not pk:
            raise self.NoPassportPkProvided()

        if not self.current_identity:
            raise self.FailedToRetrieveCurrentIdentityException()

        try:
            data = TransactionApi.create_transaction_transfer(
                request,
                self.current_identity,
                pk
            )

        except:
            raise self.FailedToConnectPassportBook()

    @detail_route()
    def redeem(
        self,
        request,
        pk=None
    ):
        if not pk:
            raise self.NoPassportPkProvided()

        if not self.current_identity:
            raise self.FailedToRetrieveCurrentIdentityException()

        collection_pk = pk[:36]
        page_number = pk[36:]

        try:
            collection_item = TransactionCollectionItem.objects.get(
                transaction_colleciton=collection_pk,
                page=int(page_number)
            )
            purchase = collection_item.transaction

        except:
            raise self.FailedToRedeemPassportOffer()

    class NoPassportPkProvided(APIException):
        status_code = 500
        default_detail = 'No Passport PK was provided.'

    class FailedToRetrieveCurrentIdentityException(APIException):
        status_code = 500
        default_detail = 'Failed to retrieve current identity.'

    class FailedToRedeemPassportOffer(APIException):
        status_code = 500
        default_detail = 'Failed to redeem passport offer.'

    class FailedToConnectPassportBook(APIException):
        status_code = 500
        default_detail = 'Failed to connect passport book.'


class PassportRedemptionApiViewSet(ApiViewSet, GetCurrentIdentityMixin):
    api_path = 'passport/redemption'
    resource_name = 'passport-connect'


class PassportApi(object):
    @staticmethod
    def _normal_redeem(
        reqeust=None,
        purchase_pk=None
    ):
        return TransactionApi.create_redemption(
            request=reqeust,
            transaction=purchase,
            current_identity=current_identity
        )

    @staticmethod
    def _complex_redeem(
        collection_pk,
        page_number
    ):
        pass

    @staticmethod
    def redeem(
        request=None,
        current_identity=None,
        purchase=None,
        collection=None,
        page_number=None
    ):
        if None is purchase:
            c
            PassportApi._normal_redeem(purchase_pk)


        return TransactionApi.create_redemption(
            request=request,
            transaction=purchase,
            current_identity=current_identity
        )

        else:
            raise Exception('Invalid Parameters.')

    @staticmethod
    def connect(
        transaction_colleciton_pk
    ):
        pass
