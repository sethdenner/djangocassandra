from django.core.management.base import BaseCommand
from optparse import make_option
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)

from django.utils.log import logging
logger = logging.getLogger(__name__)
from datetime import datetime

from knotis.contrib.product.models import Product
from knotis.contrib.inventory.models import Inventory
from knotis.contrib.offer.models import Offer, OfferPublish
from knotis.contrib.media.models import ImageInstance
from knotis.contrib.endpoint.models import Endpoint, EndpointTypes


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
            default=10,
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
        )

    def handle(
        self,
        *args,
        **options
    ):
        owner_name = options['owner']
        try:
            owner_identity = Identity.objects.get(
                name=owner_name,
                identity_type=IdentityTypes.BUSINESS
            )
        except:
            logger.exception('Cannot find owner %s' % owner_name)
            raise


        currency_name = options['currency']
        currency = Product.currency.get(currency_name)

        price = options['price']
        value = options['value']
        product = Product.objects.get_or_create_credit(
            price,
            value,
            currency.sku
        )

        print owner_name, owner_identity, product


        inventory = Inventory.objects.create_stack_from_product(
            owner_identity,
            product,
            price=value,
            unlimited=True,
        )

        split_inventory = Inventory.objects.split(
            inventory,
            owner_identity,
            1
        )
        title = options['title']

        photos = ImageInstance.objects.filter(
            owner=owner_identity,
            context='offer_banner',
        )


        offer = Offer.objects.create(
            owner=owner_identity,
            title=title,
            start_time=options['start_time'],
            end_time=options['end_time'],
            stock=None,
            unlimited=True,
            inventory=[split_inventory],
            discount_factor=price / value
        )

        offer.save()

        new_photo = ImageInstance.objects.create(
            owner=owner_identity,
            image=photos[0].image,
            related_object_id=offer.id,
            context='offer_banner',
            primary=True
        )
        endpoint_current_identity = Endpoint.objects.get(
            endpoint_type=EndpointTypes.IDENTITY,
            identity=owner_identity
        )
        OfferPublish.objects.create(
            endpoint=endpoint_current_identity,
            subject=offer,
            publish_now=True
        )

        offer.default_image = new_photo
        offer.save()

        print offer
