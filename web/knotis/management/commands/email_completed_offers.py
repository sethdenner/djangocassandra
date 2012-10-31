import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import (
    BaseCommand,
    CommandError
)
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.utils.view import format_currency
from knotis.apps.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.apps.offer.models import (
    Offer,
    OfferStatus
)


class Command(BaseCommand):
    args = '<days>'
    help = (
        'Send an email containing all of the transaction for expired offers '
        'for the past <days> days.'
    )
    
    def handle(
        self,
        *args,
        **options
    ):
        logger.info('start sending of completed offers to billing')

        try:
            offers = Offer.objects.filter(
                status=OfferStatus.COMPLETE,
            )

        except:
            raise CommandError('Offer retrieval failed')

        data = {}
        transaction_count = 0
        now = datetime.datetime.utcnow()
        
        if not args:
            days = settings.EMAIL_COMPLETED_OFFERS_INTERVAL_DAYS
        
        else:
            days = int(args[0]) 
        
        offer_min_date = (now - datetime.timedelta(days=days))
        
        logger.debug('retrieving offers since %s' % offer_min_date, )
        for offer in offers:
            if (
                not offer.end_date or 
                not offer.start_date or 
                not offer.last_purchase or 
                not offer.stock or 
                not offer.purchased
            ):
                continue 
            
            if (offer.end_date > offer_min_date and offer.end_date < now) or \
                (offer.purchased >=  offer.stock and offer.last_purchase and offer.last_purchase > offer_min_date):
                try:
                    transactions = Transaction.objects.filter(
                        offer=offer,
                        transaction_type=TransactionTypes.PURCHASE
                    )
    
                except:
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
                    
                    transaction_count += 1

        if 0 == transaction_count:
            logger.info('no new transactions')
            return

        logger.info(''.join([
            'found ',
            str(transaction_count),
            ' transactions for ',
            str(len(offers)),
            ' offers'
        ]))

        email_body = ''
        for business, offers in data.items():
            if not offers:
                continue

            email_body = ''.join([
                email_body,
                '\nTransactions for ',
                business.business_name.value,
                '\n'
            ])

            total = .0
            for offer, transactions in offers.items():
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
                        str(transaction.quantity),
                        ' for $',
                        transaction.value_formatted(),
                        '\n'
                    ])
                    total += transaction.value
            
            fee = total * .03
            grand_total = total - fee
            email_body = ''.join([
                email_body,
                '\nSub Total: $',
                format_currency(total),
                '\n3% Processing Fee: $',
                format_currency(fee),
                '\nGrand Total: $',
                format_currency(grand_total),
                '\n'
            ])

        billing_address = settings.EMAIL_BILLING_USER
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
            raise CommandError('failed to send email')

        logger.info('completed offers successfully sent to billing')
