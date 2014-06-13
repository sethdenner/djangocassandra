from django.core.management.base import BaseCommand
from optparse import make_option

from django.utils.log import logging
logger = logging.getLogger(__name__)
from datetime import datetime

from knotis.contrib.offer.api import OfferCreateApi

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--owner',
            dest='owner',
            default=None,
            help='Owner for the offer to be created.'),

        make_option('--title',
            dest='title',
            default='',
            help='Title for the offer'),

        make_option('--price',
            dest='price',
            default=10,
            type=int,
            help='Price for the offer'),

        make_option('--value',
            dest='value',
            default=20,
            type=int,
            help='Value for the offer'),

        make_option('--currency',
            dest='currency',
            default='usd',
            help='Currency for the offer'),

        make_option('--start_time',
            dest='start_time',
            default=datetime(1900, 1, 1),
            help='Start time for the offer'),

        make_option('--end_time',
            dest='end_time',
            default=None,
            help='End time for the offer'),

        make_option('--description',
            dest='description',
            default='',
            help='Description for the offer'),

        make_option('--restrictions',
            dest='restrictions',
            default='',
            help='Restrictions for the offer'),

        make_option('--is_physical',
            dest='is_physical',
            action="store_true",
            default=False,
            help='If the offer is for a physical item'),

        make_option('--stock',
            dest='stock',
            default=-1,
            type=int,
            help=''),
        )

    def handle(
        self,
        *args,
        **options
    ):
        OfferCreateApi.create_offer(**options)
