from django.core.management.base import BaseCommand
from knotis.contrib.transaction.api import (
    TransactionApi
)
from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.models import (
    IdentityIndividual,
)
import settings

from django.utils.log import logging
import csv
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        if len(args) < 3:
            raise Exception(
                ' '.join([
                    'Not enough arguements.',
                    'Usage: <neighborhood>',
                    '<provisioner email>',
                    '<number books>',
                    '<output csv>'
                ])
            )

        neighborhood = args[0]
        provision_email = args[1]
        numb_books = int(args[2])
        output_csv = args[3]
        knotis_user = KnotisUser.objects.get(username=provision_email)
        provision_user = IdentityIndividual.objects.get_individual(
            knotis_user
        )

        with open(output_csv, 'w') as f:
            csv_file = csv.writer(f)
            for book_numb in xrange(1, numb_books + 1):

                transaction_collection = None
                for (
                    transaction_collection,
                    seller,
                    page_numb,
                    promo_code
                ) in TransactionApi.create_transaction_collection(
                    neighborhood,
                    provision_user
                ):

                    csv_file.writerow([
                        neighborhood,
                        page_numb,
                        book_numb,
                        settings.BASE_URL + '/qrcode/redeem/%s/' % (seller.pk),
                        seller.redemption_code()
                    ])

                if transaction_collection is not None:
                    transaction_collection_url = settings.BASE_URL + (
                        '/qrcode/connect/%s/' % transaction_collection.pk
                    )

                    csv_file.writerow([
                        neighborhood,
                        'last_page',
                        book_numb,
                        transaction_collection_url,
                        promo_code.value.upper()
                    ])
