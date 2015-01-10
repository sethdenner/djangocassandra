from django.core.management.base import BaseCommand
from knotis.contrib.offer.api import OfferApi
from knotis.contrib.offer.models import (
    OfferCollection,
    OfferCollectionItem,
)
from optparse import make_option

from django.utils.log import logging
logger = logging.getLogger(__name__)

from csv import DictReader


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--value',
            default='150',
            help='The total value for the offer collection'
        ),
        make_option(
            '--description',
            default='Passport book!',
            help='The description for the '
        ),
        make_option(
            '--description',
            default='Passport book!',
            help='The description for the '
        ),
    )

    def handle(
        self,
        *args,
        **options
    ):
        if len(args) < 2:
            raise Exception("Not enough arguements")

        input_file = args[0]
        neighborhood = args[1]

        with open(input_file) as f:
            csv_dict = DictReader(f)

            offer_collection = OfferCollection.objects.create(
                neighborhood=neighborhood
            )
            for row in csv_dict:
                value = row.get('offer amount')
                title = '$%s credit toward any purchase' % value
                restrictions = '$%s Minimum' % row.get('minimum')
                page_num = row.get('page number', None)
                if page_num is None:
                    logger.exception('Missing page number for offer.')
                    continue
                try:
                    new_offer = OfferApi.create_offer(
                        value=float(value),
                        description=row.get('catagory'),
                        restrictions=restrictions,
                        title=title,
                        is_physical=False,
                        business_name=row.get('business name'),
                        email=row.get('email'),
                        stock=row.get('stock', 0.0),
                    )
                    OfferCollectionItem.objects.create(
                        offer=new_offer,
                        page=page_num,
                        offer_collection=offer_collection,
                    )

                except:
                    logger.exception('Failed at creating offer')

            OfferApi.create_offer(
                title=neighborhood,
                description=offer_collection.pk,
                value=options['value'],
                is_physical=False,
            )
