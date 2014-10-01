import random
import string

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings

from django.template import RequestContext

from rest_framework.response import Response
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed
)

from knotis.views import ApiModelViewSet

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.identity.models import IdentityTypes
from knotis.contrib.relation.models import Relation
from knotis.contrib.activity.models import Activity
from knotis.contrib.offer.models import Offer
from knotis.contrib.product.models import (
    Product,
    CurrencyCodes
)
from knotis.contrib.inventory.models import Inventory

from knotis.contrib.paypal.views import IPNCallbackView

from knotis.contrib.stripe.api import StripeApi

from .models import (
    Transaction,
    TransactionTypes,
    TransactionCollectionItem
)
from .views import (
    CustomerReceiptBody,
    MerchantReceiptBody
)
from .serializers import (
    TransactionSerializer
)


class PurchaseMode:
    STRIPE = 'stripe'
    FREE = 'free'
    NONE = 'none'

    CHOICES = (
        (STRIPE, 'Stripe'),
        (FREE, 'Free'),
        (NONE, 'None')
    )


class TransactionApi(object):
    @staticmethod
    def create_purchase(
        request=None,
        offer=None,
        buyer=None,
        currency=None,
        transaction_context=None,
        mode=None,
        send_email=True,
        *args,
        **kwargs
    ):

        if transaction_context is None:
            redemption_code = ''.join(
                random.choice(
                    string.ascii_uppercase + string.digits
                ) for _ in range(10)
            )

            transaction_context = '|'.join([
                buyer.pk,
                IPNCallbackView.generate_ipn_hash(buyer.pk),
                redemption_code,
                mode
            ])

        if None is mode:
            mode = PurchaseMode.NONE

        transactions = Transaction.objects.create_purchase(
            offer,
            buyer,
            currency,
            transaction_context=transaction_context,
            force_free=(mode == PurchaseMode.FREE)
        )

        if send_email:
            for t in transactions:
                if offer.owner != t.owner:
                    try:
                        user_customer = (
                            KnotisUser.objects.get_identity_user(
                                t.owner
                            )
                        )
                        customer_receipt = (
                            CustomerReceiptBody().generate_email(
                                'Knotis - Offer Receipt',
                                settings.EMAIL_HOST_USER,
                                [user_customer.username], RequestContext(
                                    request, {
                                        'transaction_id': t.pk
                                    }
                                )
                            )
                        )
                        customer_receipt.send()

                    except Exception, e:
                        # shouldn't fail if emails fail to send.
                        logger.exception(e.message)

                else:
                    try:
                        manager_email_list = []
                        manager_rels = Relation.objects.get_managers(
                            t.owner
                        )
                        for rel in manager_rels:
                            manager_user = (
                                KnotisUser.objects.get_identity_user(
                                    rel.subject
                                )
                            )
                            manager_email_list.append(
                                manager_user.username
                            )

                        merchant_receipt = (
                            MerchantReceiptBody().generate_email(
                                'Knotis - Offer Receipt',
                                settings.EMAIL_HOST_USER,
                                manager_email_list, RequestContext(
                                    request, {
                                        'transaction_id': t.pk
                                    }
                                )
                            )
                        )
                        merchant_receipt.send()

                    except Exception, e:
                        # shouldn't fail if emails fail to send.
                        logger.exception(e.message)

        if request is not None:
            Activity.purchase(request)

        return transactions

    @staticmethod
    def create_redemption(
        request=None,
        transaction=None,
        current_identity=None,
        *args,
        **kwargs
    ):
        if (
            current_identity.pk != transaction.offer.owner.pk and
            current_identity.pk != transaction.owner.pk
        ):
            raise TransactionApi.WrongOwnerException(
                'The current identity, %s, does not match the owner identity, '
                '%s' % (current_identity.pk, transaction.owner.pk)
            )

        try:
            existing_redemptions = Transaction.objects.filter(
                owner=transaction.owner,
                transaction_type=TransactionTypes.REDEMPTION,
                transaction_context=transaction.transaction_context
            )

        except Exception, e:
            logger.exception('failed to check for existing redemptions.')
            raise e

        if (len(existing_redemptions)):
            raise TransactionApi.AlreadyRedeemedException(
                'This purchase has already been redeemed.'
            )

        try:
            redemptions = Transaction.objects.create_redemption(transaction)

        except Exception, e:
            logger.exception('failed to create redemption')
            raise e

        Activity.redeem(request)

        return redemptions

    class WrongOwnerException(Exception):
        pass

    class AlreadyRedeemedException(Exception):
        pass

    @staticmethod
    def transfer_transaction_collection(
        request=None,
        new_owner=None,
        transaction_collection=None,
    ):
        if new_owner.identity_type != IdentityTypes.INDIVIDUAL:
            raise TransactionApi.WrongIdentityTypeException(
                'Idenity %s is not an individual.' % new_owner
            )

        transaction_collection_items = (
            TransactionCollectionItem.objects.filter(
                transaction_collection=transaction_collection
            )
        )

        if len(transaction_collection_items) < 1:
            raise TransactionApi.NoTransactionCollectionItemsException(
                'There where no TransactionCollectionItems '
                'attached to this collection.'
            )
        '''
        Test if this transaction collection has already been transfered.
        !IMPORTANT NOTE!:This assumes that if one transaction in the collection
        has been transfered then all of them have been.
        '''
        test_transaction = transaction_collection_items[0].transaction
        other_transfers = Transaction.objects.filter(
            transaction_type=TransactionTypes.TRANSACTION_TRANSFER,
            transaction_context=(
                test_transaction.transaction_context
            ),
            offer=test_transaction.offer,
        )
        if len(other_transfers) != 0:
            raise TransactionApi.TransactionCollectionAlreadyTransfered(
                "Already transfered this transaction collection!"
            )

        transactions = []
        for t in transaction_collection_items:
            for owner in [new_owner, t.transaction.owner]:
                transactions.append(
                    Transaction.objects.create(
                        owner=owner,
                        transaction_type=TransactionTypes.TRANSACTION_TRANSFER,
                        offer=t.transaction.offer,
                        transaction_context=t.transaction.transaction_context
                    )
                )

            t.transaction.owner = new_owner
            t.transaction.save()

        Activity.redeem(request)

        return transactions

    class WrongIdentityTypeException(Exception):
        pass

    class NoTransactionCollectionItemsException(Exception):
        pass

    class TransactionCollectionAlreadyTransfered(Exception):
        pass


class PurchaseApiModelViewSet(ApiModelViewSet, GetCurrentIdentityMixin):
    api_path = 'transaction/purchase'
    resource_name = 'purchase'

    model = Transaction
    queryset = Transaction.objects.filter(
        transaction_type=TransactionTypes.PURCHASE
    )
    serializer_class = TransactionSerializer

    def initial(
        self,
        request,
        *args,
        **kwargs
    ):
        super(PurchaseApiModelViewSet, self).initial(
            request,
            *args,
            **kwargs
        )

        self.get_current_identity(request)

    def get_queryset(self):
        if self.current_identity:
            return self.queryset.filter(owner=self.current_identity)

        else:
            return self.model.objects.none()

    def create(
        self,
        request
    ):
        if not self.current_identity:
            raise self.FailedToRetrieveCurrentIdentityException()

        offer_pk = request.DATA.get('offer')
        mode = request.DATA.get('mode', 'none')

        try:
            offer = Offer.objects.get(pk=offer_pk)

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToRetrieveOfferException()

        redemption_code = ''.join(
            random.choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(10)
        )
        transaction_context = '|'.join([
            self.current_identity.pk,
            IPNCallbackView.generate_ipn_hash(self.current_identity.pk),
            redemption_code,
            mode
        ])

        try:
            amount = offer.price_discount()

        except:
            raise self.InvalidChargeAmountException()

        if amount < 0.:
            raise self.InvalidChargeAmountException()

        if PurchaseMode.STRIPE == mode:
            try:
                charge = StripeApi.create_charge(
                    self.current_identity,
                    amount
                )

            except Exception, e:
                logger.exception(e.message)
                raise self.FailedToCreateStripeChargeException()

        else:
            charge = None

        if amount > 0.:
            try:
                usd = Product.currency.get(CurrencyCodes.USD)
                buyer_usd = Inventory.objects.create_stack_from_product(
                    self.current_identity,
                    usd,
                    stock=amount,
                    get_existing=True
                )

            except Exception, e:
                logger.exception(e.message)

                if None is not charge:
                    if PurchaseMode.STRIPE == mode:
                        try:
                            charge.refund()
                            charge = None

                        except Exception, e:
                            # THIS IS BAD NEED TO MANUALLY REFUND USER
                            logger.exception(''.join([
                                'THIS IS SUPER BAD! NEED TO MANUALLY REFUND USER ',
                                self.current_identity.name,
                                ' (',
                                self.current_identity.pk,
                                ' ) in the amount of $',
                                amount
                            ]))

                raise self.FailedToDepositCurrencyException()

        else:
            buyer_usd = None

        try:
            purchases = TransactionApi.create_purchase(
                request=request,
                offer=offer,
                buyer=self.current_identity,
                currency=buyer_usd,
                transaction_context=transaction_context
            )

        except Exception, e:
            logger.exception(e.message)

            if None is not charge:
                if PurchaseMode.STRIPE == mode:
                    try:
                        charge.refund()

                    except Exception, e:
                        # THIS IS BAD NEED TO MANUALLY REFUND USER
                        logger.exception(''.join([
                            'THIS IS SUPER BAD! NEED TO MANUALLY REFUND USER ',
                            self.current_identity.name,
                            ' (',
                            self.current_identity.pk,
                            ' ) in the ammount of $',
                            amount
                        ]))

            raise self.FailedToCreatePurchaseException()

        my_purchase = None
        for p in purchases:
            if p.owner.pk == self.current_identity.pk:
                my_purchase = p
                break

        serializer = TransactionSerializer(my_purchase)
        return Response(serializer.data)

    def list(
        self,
        request
    ):
        if not self.current_identity:
            raise self.FailedToRetrieveCurrentIdentityException()

        try:
            purchases = Transaction.objects.filter(
                owner=self.current_identity,
                transaction_type=TransactionTypes.PURCHASE
            )

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToRetrievePurchaseException()

        unredeemed_purchases = []
        for purchase in purchases:
            if not purchase.has_redemptions():
                unredeemed_purchases.append(purchase)

        serializer = self.serializer_class(unredeemed_purchases, many=True)
        return Response(serializer.data)

    def update(
        self,
        request,
        pk=None
    ):
        raise MethodNotAllowed(request.method)

    def partial_update(
        self,
        request,
        pk=None
    ):
        raise MethodNotAllowed(request.method)

    def destroy(
        self,
        request,
        pk=None
    ):
        raise MethodNotAllowed(request.method)

    class FailedToRetrieveCurrentIdentityException(APIException):
        status_code = 500
        default_detail = 'Failed to retrieve current identity.'

    class FailedToRetrieveOfferException(APIException):
        status_code = 500
        default_detail = 'Failed to get the offer requested.'

    class FailedToCreateStripeChargeException(APIException):
        status_code = 500
        default_detail = 'Failed to call to create Stripe charge.'

    class FailedToDepositCurrencyException(APIException):
        status_code = 500
        default_detail = 'Failed to deposit currency.'

    class FailedToCreatePurchaseException(APIException):
        status_code = 500
        default_detail = 'Failed to create purchase.'

    class InvalidChargeAmountException(APIException):
        status_code = 500
        default_detail = 'Charge amount must be a positive int or float.'


class RedemptionApiModelViewSet(ApiModelViewSet, GetCurrentIdentityMixin):
    api_path = 'transaction/redemption'
    resource_name = 'redemption'

    model = Transaction
    queryset = Transaction.objects.filter(
        transaction_type=TransactionTypes.REDEMPTION
    )
    serializer_class = TransactionSerializer

    def initial(
        self,
        request,
        *args,
        **kwargs
    ):
        super(RedemptionApiModelViewSet, self).initial(
            request,
            *args,
            **kwargs
        )

        self.get_current_identity(request)

    def get_queryset(self):
        if self.current_identity:
            return self.queryset.filter(owner=self.current_identity)

        else:
            return self.model.objects.none()

    def create(
        self,
        request
    ):
        if not self.current_identity:
            raise self.FailedToRetrieveCurrentIdentityException()

        transaction = request.DATA.get('transaction')
        if not transaction:
            raise self.CannotCreateRedemptionWithoutPurchaseException()

        try:
            transaction = Transaction.objects.get(pk=transaction)

        except Exception, e:
            logger.exception(e)
            raise self.FailedToRetrievePurchaseException()

        try:
            redemptions = TransactionApi.create_redemption(
                request,
                transaction,
                self.current_identity
            )

        except Exception, e:
            logger.exception(e)

            raise self.FailedToCreateRedemptionException()

        my_redemption = None
        for r in redemptions:
            if r.owner.pk == self.current_identity.pk:
                my_redemption = r
                break

        serializer = TransactionSerializer(my_redemption)
        return Response(serializer.data)

    class CannotCreateRedemptionWithoutPurchaseException(APIException):
        status_code = 500
        default_detail = (
            'Cannot create redemption without an existing purchase.'
        )

    class FailedToRetrievePurchaseException(APIException):
        status_code = 500
        default_detail = (
            'Failed to find purchase matching pk'
        )

    class FailedToCreateRedemptionException(APIException):
        status_code = 500
        default_detail = 'Failed to create redemption.'
