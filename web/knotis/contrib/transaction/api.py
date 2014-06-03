import random
import string

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404
from django.conf import settings

from django.template import RequestContext

from rest_framework.exceptions import MethodNotAllowed
from rest_framework.renderers import JSONRenderer

from knotis.views import ApiModelViewSet

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.models import Identity
from knotis.contrib.relation.models import Relation
from knotis.contrib.activity.models import Activity
from knotis.contrib.offer.models import Offer
from knotis.contrib.product.models import (
    Product,
    CurrencyCodes
)
from knotis.contrib.inventory.models import Inventory

from knotis.contrib.paypal.views import IPNCallbackView

from .models import (
    Transaction,
    TransactionTypes
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
    NONE = 'none'

    CHOICES = (
        (STRIPE, 'Stripe'),
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
        *args,
        **kwargs
    ):
        if None is mode:
            mode = PurchaseMode.NONE

        transactions = Transaction.objects.create_purchase(
            offer,
            buyer,
            currency,
            transaction_context=transaction_context
        )

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
                    #shouldn't fail if emails fail to send.
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
                    #shouldn't fail if emails fail to send.
                    logger.exception(e.message)

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
        if current_identity.pk != transaction.owner.pk:
            raise WrongOwnerException((
                'The current identity, %s, does not match the owner identity, '
                '%s' % (current_identity.pk, transaction.owner.pk)
            ))

        try:
            redemptions = Transaction.objects.create_redemption(transaction)

        except Exception, e:
            logger.exception('failed to create redemption')
            raise e

        Activity.redeem(request)

        return redemptions


class PurchaseApiModelViewSet(ApiModelViewSet):
    api_path = 'transaction/purchase'
    resource_name = 'purchase'

    model = Transaction
    queryset = Transaction.objects.filter(
        transaction_type=TransactionTypes.PURCHASE
    )
    serializer_class = TransactionSerializer

    def create(
        self,
        request
    ):
        current_identity_pk = request.DATA.get('current_identity')
        current_identity = get_object_or_404(
            Identity,
            pk=current_identity_pk
        )
        offer_pk = request.DATA.get('offer')
        offer = get_object_or_404(
            Offer,
            pk=offer_pk
        )
        redemption_code = ''.join(
            random.choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(10)
        )
        mode = request.DATA.get('mode', 'none')
        transaction_context = '|'.join([
            current_identity.pk,
            IPNCallbackView.generate_ipn_hash(current_identity.pk),
            redemption_code,
            mode
        ])

        usd = Product.currency.get(CurrencyCodes.USD)
        buyer_usd = Inventory.objects.create_stack_from_product(
            current_identity,
            usd,
            stock=amount,
            get_existing=True
        )

        purchases = TransactionApi.create_purchase(
            request=request,
            offer=offer.pk,
            buyer=current_identity,
            currency=buyer_usd,
            transaction_context=transaction_context
        )

        my_purchase = None
        for p in purchases:
            if p.owner.pk == current_identity.pk:
                my_purchase = p
                break

        serializer = TransactionSerializer(my_purchase)
        return JSONRenderer().render(serializer.data)

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


class RedemptionApiModelViewSet(ApiModelViewSet):
    api_path = 'transaction/purchase'
    resource_name = 'purchase'

    model = Transaction
    queryset = Transaction.objects.filter(
        transaction_type=TransactionTypes.REDEMPTION
    )
    serializer_class = TransactionSerializer


class WrongOwnerException(Exception):
    pass
