from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings

from django.template import RequestContext

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.relation.models import Relation
from knotis.contrib.activity.models import Activity

from models import Transaction
from views import (
    CustomerReceiptBody,
    MerchantReceiptBody
)


class TransactionApi(object):
    @staticmethod
    def create_purchase(
        request=None,
        offer=None,
        buyer=None,
        currency=None,
        transaction_context=None,
        *args,
        **kwargs
    ):
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

class WrongOwnerException(Exception):
        pass
