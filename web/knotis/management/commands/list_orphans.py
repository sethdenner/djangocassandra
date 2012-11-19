from django.utils import log
logger = log.getLogger(__name__)

from django.core.management.base import (
    BaseCommand,
    CommandError
)

from knotis.apps.business.models import Business
from knotis.apps.offer.models import Offer
from knotis.apps.transaction.models import Transaction

class Command(BaseCommand):
    args = '<b(business)|o(offer)|t(transaction)>'
    help = (
        'lists orphaned objects for each type'
    )
    
    def handle(
        self,
        *args,
        **options
    ):
        if not args:
            raise CommandError('no arguments')
        
        otypes = list(args[0])
        
        if 'b' in otypes:
            try:
                businesses = Business.objects.all()
                orphans = []
                for business in businesses:
                    if not business.user:
                        orphans.append(business)
                    
                if orphans:
                    logger.info('businesses with no user:')
                    for business in orphans:
                        logger.info('%s (%s) <%s>' % (
                            business.business_name.value, 
                            business.backend_name,
                            business.id
                        ))
                        
            except:
                logger.exception('error finding orphaned businesses')
                
        if 'o' in otypes:
            try:
                offers = Offer.objects.all()
                orphans = []
                for offer in offers:
                    if not offer.business:
                        orphans.append(offer)
                        
                if orphans:
                    logger.info('offers with no business:')
                    for offer in orphans:
                        logger.info('%s <%s>' % (
                            offer.title_formatted(), 
                            offer.id
                        ))
                        
            except:
                logger.exception('error finding orphaned offers')
                        
        if 't' in otypes:
            try:
                transactions_no_b = []
                transactions_no_u = []
                transactions_no_bu = []
                
                transactions = Transaction.objects.all()
                for transaction in transactions:
                    if not transaction.user and not transaction.business:
                        transactions_no_bu.append(transaction)
                        
                    elif not transaction.user:
                        transactions_no_u.append(transaction)
                        
                    elif not transaction.business:
                        transactions_no_b.append(transaction)
                
                if transactions_no_b:
                    logger.info('transactions with no business:')
                    for transaction in transactions_no_b:
                        logger.info('%s %s <%s>' % (
                            transaction.user,
                            transaction.value_formatted(),
                            transaction.id
                        ))

                if transactions_no_u:
                    logger.info('transactions with no user:')
                    for transaction in transactions_no_b:
                        logger.info('%s %s <%s>' % (
                            transaction.business.backend_name,
                            transaction.value_formatted(),
                            transaction.id
                        ))
                        
                if transactions_no_bu:
                    logger.info('transactions with no user and no business')
                    for transaction in transactions_no_bu:
                        logger.info('%s <%s>' % (
                            transaction.value_formatted(),
                            transaction.id
                        ))
                        
            except:
                logger.exception('error finding orphaned offers')
                        