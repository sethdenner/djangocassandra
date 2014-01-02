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


class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        purchases = Transaction.objects.filter(transaction_type=TransactionTypes.PURCHASE)
        offer_purchase_counters = {}
        for purchase in purchases:
            if not purchase.offer:
                continue
        
            if not purchase.offer.last_purchase or purchase.pub_date > purchase.offer.last_purchase:
                purchase.offer.last_purchase = purchase.pub_date
                purchase.offer.save()
        
            if offer_purchase_counters.get(purchase.offer):
                offer_purchase_counters[purchase.offer] += 1
            
            else:
                offer_purchase_counters[purchase.offer] = 1

        for offer, purchased in offer_purchase_counters.items():
            offer.purchased = purchased
            offer.save()
            