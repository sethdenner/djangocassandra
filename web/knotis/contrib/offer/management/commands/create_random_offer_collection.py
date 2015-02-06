import settings

from django.core.management.base import BaseCommand
from optparse import make_option

from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.offer.models import (
    OfferCollection,
)
from knotis.contrib.offer.api import (
    OfferApi,
)
from knotis.contrib.identity.models import IdentityEstablishment


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--owner',
            default='Knotis',
            help='The owner of the random offer.'
        ),
        make_option(
            '--use_once',
            default=True,
            help='One time random offers.'
        ),
        make_option(
            '--count',
            default='1',
            help='Number of random offers to provision.'
        ),
        make_option(
            '--output_csv',
            default='random_offers.csv',
            help='The output csv for the random offers.'
        ),
    )

    def handle(
        self,
        *args,
        **options
    ):

        try:
            owner = IdentityEstablishment.objects.get(
                name=options.get('owner')
            )
        except:
            raise Exception(
                'Failed to find establishment %s' % options.get('owner')
            )

        try:
            offer_collection_list = [
                OfferCollection.objects.get(
                    neighborhood=neighborhood
                ) for neighborhood in args
            ]
        except:
            raise Exception(
                'Failed to find one or more of the neighborhood in ' % args
            )

        count = int(options.get('count'))
        with open(options.get('output_csv'), 'w') as output:
            output.write('%s,%s,%s\n' % (
                'page number', 'qrcode url', 'promocode'
            ))

            for x in xrange(1, count+1):
                offer, promo_code = OfferApi.create_random_offer_collection(
                    offer_collection_list,
                    owner=owner,
                    use_once=False
                )
                qrcode_url = settings.BASE_URL + (
                    '/qrcode/random/%s/' % offer.pk
                )
                output.write('%s,%s,%s\n' % (
                    x, qrcode_url, promo_code.value
                ))
