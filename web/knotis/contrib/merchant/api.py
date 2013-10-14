from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponseServerError

from knotis.views import ApiView

from knotis.contrib.identity.models import Identity
from knotis.contrib.transaction.models import (
    Transaction,
    TransactionItem,
    TransactionTypes
)


class RedemptionApi(ApiView):
    api_url = 'merchant/redeem'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        try:
            current_identity_id = request.session.get('current_identity_id')
            current_identity = Identity.objects.get(pk=current_identity_id)

        except Exception, e:
            logger.exception('failed to get current identity')
            return HttpResponseServerError(e.message)

        try:
            transaction_context = request.POST.get('transaction_context')
            transactions = Transaction.objects.filter(
                transaction_context=transaction_context
            )

        except Exception, e:
            logger.exception('failed to get outstanding purchase')
            return HttpResponseServerError(e.message)

        purchase = None
        redemption = None
        for t in transactions:
            if (
                current_identity != t.owner and
                t.transaction_type == TransactionTypes.PURCHASE
            ):
                purchase = t

            elif (
                current_identity != t.owner and
                t.transaction_type == TransactionTypes.REDEMPTION
            ):
                redemption = t

            if purchase and redemption:
                break

        if purchase and redemption:
            return self.generate_response({
                'errors': {
                    'no-field': 'This purchase has already been redeemed.'
                }
            })

        if not purchase:
            return self.generate_respones({
                'errors': {
                    'no-field': (
                        'There is no purchase for '
                        'the parameters provided.'
                    )
                }
            })

        # Always redeem all inventory for now.
        try:
            transaction_items = TransactionItem.objects.filter(
                transaction=purchase
            )

            inventory = []
            for item in transaction_items:
                inventory.append(item.inventory)

        except Exception, e:
            logger.exception('failed to get invetory to redeem.')
            return HttpResponseServerError(e.message)

        try:
            redemptions = Transaction.objects.create_redemption(
                purchase.offer,
                purchase.owner,
                inventory,
                purchase.transaction_context
            )

        except Exception, e:
            logger.exception('Failed to create redemption')
            return HttpResponseServerError(e.message)

        return self.generate_response({
            'message': 'Purchase redeemed.',
            'transaction_ids': [t.id for t in redemptions],
            'transaction_context': transaction_context
        })
