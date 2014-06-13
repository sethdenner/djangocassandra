from django.core.management.base import BaseCommand
from knotis.contrib.offer.api import OfferCreateApi

from csv import DictReader

class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        if not args:
            raise Exception("Not enough arguements")

        with open(args[0]) as f:
            csv_dict = DictReader(f)
            for row in csv_dict:
                value = row.get('offer amount')
                OfferCreateApi.create_offer(
                    value=value,
                    description=row.get('catagory'),
                    restrictions=row.get('restrictions'),
                    is_physical=False,
                    owner=row.get('business name'),
                    email=row.get('email'),
                )
