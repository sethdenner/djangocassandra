from django.utils.log import logging
logger = logging.getLogger(__name__)

from rest_framework.decorators import action
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from knotis.views import ApiViewSet

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.transaction.models import (
    TransactionCollection,
    TransactionCollectionItem
)
from knotis.contrib.transaction.serializers import TransactionSerializer


class PassportApi(object):
    @staticmethod
    def retrieve_coupon(
        collection_pk,
        page_number
    ):
        collection = TransactionCollection.objects.get(
            pk=collection_pk
        )

        collection_item = TransactionCollectionItem.objects.get(
            transaction_collection=collection,
            page=page_number
        )

        return collection_item.transaction

    @staticmethod
    def connect(
        consumer,
        transaction_collection_pk,
        request=None
    ):
        transaction_collection = TransactionCollection.objects.get(
            pk=transaction_collection_pk
        )

        return TransactionApi.transfer_transaction_collection(
            consumer,
            transaction_collection,
            request=request
        )

    @staticmethod
    def redeem(
        redeemer,
        transaction_collection_pk,
        page_number,
        request=None
    ):
        transaction = PassportApi.retrieve_coupon(
            transaction_collection_pk,
            page_number
        )

        return TransactionApi.create_redemption(
            request,
            transaction,
            redeemer
        )


class PassportApiViewSet(ApiViewSet, GetCurrentIdentityMixin):
    api_path = 'passport'
    resource_name = 'passport'

    serializer_class = TransactionSerializer

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

    @action(methods=['put'])
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
            transfers = PassportApi.connect(
                self.current_identity,
                pk,
                request=request
            )

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToConnectPassportBook()

        '''
        Only return the transfer that belongs to the current identity
        '''
        transfer = None
        for t in transfers:
            if t.owner_id == self.current_identity.pk:
                transfer = t
                break

        serializer = self.serializer_class(transfer)
        return Response(serializer.data)


class PassportCouponApiRouter(DefaultRouter):
    def get_lookup_regex(
        self,
        viewset,
        lookup_prefix=''
    ):
        base_regex = super(PassportCouponApiRouter, self).get_lookup_regex(
            viewset,
            lookup_prefix=lookup_prefix
        )

        return '/'.join([
            base_regex,
            '(?P<page_number>\d+)'
        ])


class PassportCouponApiViewSet(ApiViewSet, GetCurrentIdentityMixin):
    api_path = 'passport'
    resource_name = 'passport'
    router_class = PassportCouponApiRouter

    serializer_class = TransactionSerializer

    def get_object(
        self,
        queryset=None
    ):
        collection_pk = self.kwargs.get(self.lookup_field, None)
        page_number = self.kwargs.get('page_number', None)

        return PassportApi.retrieve_coupon(
            collection_pk,
            page_number
        )

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

    @action(methods=['put'])
    def redeem(
        self,
        request,
        pk=None,
        page_number=None
    ):
        if None is pk:
            raise self.NoPassportPkProvided()

        if None is page_number:
            raise self.NoPageNumberProvided()

        if not self.current_identity:
            raise self.FailedToRetrieveCurrentIdentityException()

        try:
            redemptions = PassportApi.redeem(
                self.current_identity,
                pk,
                page_number,
                request=request
            )

        except Exception, e:
            logger.exception(e.message)

            raise self.FailedToRedeemPassportOffer()

        '''
        Only return the redemption that belongs to the current identity
        '''
        redemption = None
        for r in redemptions:
            if r.owner_id == self.current_identity.pk:
                redemption = r
                break

        serializer = self.serializer_class(redemption)
        return Response(serializer.data)

    class NoPassportPkProvided(APIException):
        status_code = 500
        default_detail = 'No Passport PK was provided.'

    class NoPageNumberProvided(APIException):
        status_code = 500
        default_detail = 'No Passport page number was provided.'

    class FailedToRetrieveCurrentIdentityException(APIException):
        status_code = 500
        default_detail = 'Failed to retrieve current identity.'

    class FailedToRedeemPassportOffer(APIException):
        status_code = 500
        default_detail = 'Failed to redeem passport offer.'

    class FailedToConnectPassportBook(APIException):
        status_code = 500
        default_detail = 'Failed to connect passport book.'
