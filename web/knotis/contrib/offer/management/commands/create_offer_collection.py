from django.core.management.base import BaseCommand
from knotis.contrib.offer.api import OfferCreateApi
from knotis.contrib.offer.models import OfferCollection

from django.utils.log import logging
logger = logging.getLogger(__name__)

from csv import DictReader

class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        if not args:
            raise Exception("Not enough arguements")

        input_file = args[0]
        with open(input_file) as f:
            csv_dict = DictReader(f)
            page_num = 1
            for row in csv_dict:
                value = row.get('offer amount')
                try:
                    new_offer = OfferCreateApi.create_offer(
                        dark_offer=True,
                        create_business=True,
                        value=float(value),
                        description=row.get('catagory'),
                        restrictions=row.get('restrictions'),
                        is_physical=False,
                        business_name=row.get('business name'),
                        email=row.get('email'),
                        stock=row.get('stock'),
                        currency='usd',
                    )
                    OfferCollection.objects.create(
                        offer=new_offer,
                        page=page_num,
                        neighborhood=row.get('neighborhood', '')
                    )
                    page_num += 1

                except:
                    logger.exception('Failed at creating offer')
