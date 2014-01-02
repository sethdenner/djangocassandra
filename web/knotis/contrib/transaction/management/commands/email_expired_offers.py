from django.core.mail import send_mail
from django.core.management.base import (
    BaseCommand,
    CommandError
)
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.contrib.offer.models import (
    Offer,
    OfferStatus
)


class Command(BaseCommand):
    def handle(
        self,
        * args,
        **options
    ):
        logger.info('start sending of completed offers to billing')

        try:
            offers = Offer.objects.filter(
                status=OfferStatus.COMPLETE,
            )

        except:
            logger.exception()
            raise CommandError('Offer retrieval failed')

        data = {}
        transaction_count = 0
        for offer in offers:
            try:
                transactions = Transaction.objects.filter(
                    offer=offer,
                    transaction_types=TransactionTypes.PURCHASE
                )
                transaction_count += len(transactions)

            except:
                logger.exception()
                raise CommandError('Transaction retrieval failed')

            if not transactions:
                continue

            for transaction in transactions:
                if not data.get(transaction.business):
                    data[transaction.business] = {}

                if not data.get(transaction.business).get(transaction.offer):
                    data[transaction.business][transaction.offer] = []

                data[transaction.business][transaction.offer].append(
                    transaction
                )

        logger.info(''.join([
            'found ',
            transaction_count,
            'transactions for ',
            len(offers),
            'offers'
        ]))

        email_body = ''
        for business, offers in data.items():
            if not offers:
                continue

            email_body = ''.join([
                email_body,
                'Transactions for ',
                business.business_name.value,
                '\n'
            ])

            for offer, transactions in offers:
                email_body = ''.join([
                    email_body,
                    'for offer ',
                    offer.title_formatted(),
                    '\n'
                ])

                for transaction in transactions:
                    email_body = ''.join([
                        email_body,
                        'by ',
                        transaction.user.username,
                        ': ',
                        transaction.quantity,
                        ' for $',
                        transaction.value
                    ])

        billing_address = 'billing@knotis.com'
        subject = 'Completed Offers'

        try:
            send_mail(
                subject,
                email_body,
                billing_address,
                [billing_address],
                fail_silently=False
            )

        except:
            logger.exception()
            raise CommandError('failed to send email')

        logger.info('completed offers successfully sent to billing')
