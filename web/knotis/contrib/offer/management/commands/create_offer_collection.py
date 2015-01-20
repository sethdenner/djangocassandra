from django.core.management.base import BaseCommand
from knotis.contrib.offer.api import OfferApi
from knotis.contrib.offer.models import (
    OfferTypes,
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
            default=450,
            help='The total value for the offer collection'
        ),
        make_option(
            '--description',
            default='Passport book!',
            help='The description for the passport book'
        ),
        make_option(
            '--price',
            default=15,
            help='The price for the passport book.'
        ),
        make_option(
            '--owner',
            default='Knotis',
            help='The owner of the new passport book.'
        ),
    )

    def handle(
        self,
        *args,
        **options
    ):
        if len(args) < 2:
            raise Exception("Not enough arguments")

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
                        description=row.get('category'),
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

            passport_offer = OfferApi.create_offer(
                title=neighborhood,
                business_name=options['owner'],
                description=offer_collection.pk,
                offer_type=OfferTypes.DIGITAL_OFFER_COLLECTION,
                value=float(options['value']),
                price=float(options['price']),
                is_physical=False,
            )
            passport_offer.active = True
            passport_offer.published = True
            passport_offer.save()
