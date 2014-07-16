from django.core.management.base import BaseCommand
from knotis.contrib.offer.models import OfferCollection
from knotis.contrib.identity.models import IdentityBusiness
from knotis.contrib.transaction.models import (
    TransactionCollection,
    TransactionTypes,
    Transaction
)
from knotis.contrib.paypal.views import IPNCallbackView

from django.utils.log import logging
import random
import string
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        if len(args) < 2:
            raise Exception("Not enough arguements")

        neighborhood = args[0]
        output_csv = args[1]
        with open(output_csv) as f:
            offer_collection = OfferCollection.objects.filter(neighborhood=neighborhood)

            knotis_passport = IdentityBusiness.objects.get(name='knotis_passport')
            for i in offer_collection:
                redemption_code = ''.join(
                    random.choice(
                        string.ascii_uppercase + string.digits
                    ) for _ in range(10)
                )

                transaction_context = '|'.join([
                    knotis_passport.pk,
                    IPNCallbackView.generate_ipn_hash(knotis_passport.pk),
                    redemption_code,
                    'none'
                ])
                new_transaction = Transaction.objects.create(
                    owner=knotis_passport,
                    transaction_type=TransactionTypes.DARK_PURCHASE,
                    transaction_context=transaction_context,
                    offer=i.offer,
                )

                TransactionCollection.objects.create(
                    transaction=new_transaction,
                    neighborhood=neighborhood,
                    page=i.page
                )
