from django.utils.log import logging
logger = logging.getLogger(__name__)

from rest_framework.decorators import action
from rest_framework.routers import DefaultRouter
from rest_framework.exceptions import APIException

from knotis.views import ApiViewSet

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.transaction.models import (
    TransactionCollection,
    TransactionCollectionItem
)


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

        return TransactionApi.create_transaction_transfer(
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
            data = PassportApi.connect(
                self.current_identity,
                pk,
                request=request
            )

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToConnectPassportBook()


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
        if not pk:
            raise self.NoPassportPkProvided()

        if not self.current_identity:
            raise self.FailedToRetrieveCurrentIdentityException()

        try:
            PassportApi.redeem(
                self.current_identity,
                pk,
                page_number,
                request=request
            )

        except Exception, e:
            logger.exception(e.message)

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
