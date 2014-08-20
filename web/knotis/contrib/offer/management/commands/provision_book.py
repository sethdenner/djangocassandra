from django.core.management.base import BaseCommand
from knotis.contrib.offer.models import (
    OfferCollection,
    OfferCollectionItem,
)
from knotis.contrib.identity.models import Identity
from knotis.contrib.transaction.models import (
    TransactionCollection,
    TransactionCollectionItem,
    Transaction
)
from knotis.contrib.product.models import (
    Product,
    CurrencyCodes,
)
from knotis.contrib.inventory.models import Inventory
from knotis.contrib.paypal.views import IPNCallbackView
import settings

from django.utils.log import logging
import random
import string
import csv
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        if len(args) < 3:
            raise Exception("Not enough arguements")

        neighborhood = args[0]
        provision_user = args[1]
        numb_books = int(args[2])
        output_csv = args[3]

        offer_collection = OfferCollection.objects.filter(
            neighborhood=neighborhood
        ).order_by('-pub_date')[0]

        offer_collection_items = OfferCollectionItem.objects.filter(
            offer_collection=offer_collection
        ).order_by('page')

        knotis_passport = Identity.objects.get(name=provision_user)

        usd = Product.currency.get(CurrencyCodes.USD)
        buyer_usd = Inventory.objects.get_stack(
            knotis_passport,
            usd,
            create_empty=True
        )

        with open(output_csv, 'w') as f:
            csv_file = csv.writer(f)
            for book_numb in xrange(1, numb_books + 1):
                transaction_collection = TransactionCollection.objects.create(
                    neighborhood=neighborhood
                )

                for i in offer_collection_items:
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

                    transactions = Transaction.objects.create_purchase(
                        offer=i.offer,
                        buyer=knotis_passport,
                        currency=buyer_usd,
                        transaction_context=transaction_context
                    )

                    seller_transaction = filter(
                        lambda x: x.owner != knotis_passport,
                        transactions)[0]

                    TransactionCollectionItem.objects.create(
                        transaction_collection=transaction_collection,
                        transaction=seller_transaction,
                        page=i.page,
                    )

                    csv_file.writerow([
                        neighborhood,
                        i.page,
                        book_numb,
                        '%s/%s' % (transaction_collection.pk, i.page),
                        settings.BASE_URL + '/qrcode/coupon/%s/%s' % (
                            transaction_collection.pk,
                            i.page)
                    ])

                csv_file.writerow([
                    neighborhood,
                    'last_page',
                    book_numb,
                    transaction_collection.pk,
                    settings.BASE_URL + (
                        '/qrcode/connect/%s' % transaction_collection.pk)
                ])
