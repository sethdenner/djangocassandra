import csv
import random
import string
import urllib
import os

from django.conf import settings
from django.utils import log
logger = log.getLogger(__name__)
from django.utils.http import urlquote_plus

from django.core.management.base import (
    BaseCommand,
    CommandError
)

from knotis.contrib.auth.api import AuthUserApi
from knotis.contrib.identity.api import IdentityBusinessApi
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.contrib.qrcode.models import Qrcode


class Command(BaseCommand):
    args = '<csv_file>'
    help = (
        'Imports business profiles from a csv file. Required columns are:\n'
        '    * Business - The businesses name.\n'
        '    * Contact - The name of the manager or business owner.\n'
        '    * Contact Email - The email address of the Contact.\n'
        '    * Phone - The phone number of the establishment.\n'
        '    * Website - A URL that the business wants on their profile.\n'
        '    * Address - The steet address of the establishment.\n'
    )

    def handle(
        self,
        *args,
        **options
    ):
        if not args:
            raise CommandError('No file specified')

        if not os.path.exists('./merchant-qrcodes'):
            os.makedirs('./merchant-qrcodes')

        try:
            csv_file = open(
                args[0],
                'rb'
            )
            csv_reader = csv.reader(
                csv_file,
                delimiter=',',
                quotechar='"'
            )

        except:
            msg = 'failed to load file %s' % args[0]
            logger.exception(msg)
            raise CommandError(msg)

        class Columns:
            BUSINESS_NAME = 'business'
            MANAGER_NAME = 'contact'
            MANAGER_EMAIL = 'contact email'
            MANAGER_PHONE = 'phone'
            BUSINESS_WEBSITE = 'website'
            BUSINESS_ADDRESS = 'address'

        DEFAULT_EMAIL_TEMPLATE = 'maps+%s@knotis.com'

        column_row = csv_reader.next()

        column_index = 0
        column_map = {}
        for column in column_row:
            column_map[column_index] = column.lower()
            column_index += 1

        creation_counter = 0
        for row in csv_reader:
            column_index = 0
            merchant_data = {}

            for column in row:
                merchant_data[
                    column_map[column_index]
                ] = column
                column_index += 1

            business_name = merchant_data.get(Columns.BUSINESS_NAME)
            manager_name = merchant_data.get(Columns.MANAGER_NAME)
            manager_email = merchant_data.get(Columns.MANAGER_EMAIL)
            manager_phone = merchant_data.get(Columns.MANAGER_PHONE)
            business_website = merchant_data.get(Columns.BUSINESS_WEBSITE)
            business_address = merchant_data.get(Columns.BUSINESS_ADDRESS)

            if not business_name:
                logger.error(
                    'Come on, at least need a business name '
                    'to have a valid row. Skipping.'
                )
                continue

            if not manager_email:
                manager_email = DEFAULT_EMAIL_TEMPLATE % business_name.replace(
                    ' ', ''
                ).lower()

            try:
                user, identity, errors = AuthUserApi.create_user(**{
                    'email': manager_email,
                    'password': ''.join(random.choice(
                        string.printable
                    ) for _ in range(16)),
                    'send_validation': False
                })
                identity.name = manager_name
                identity.save()

            except Exception, e:
                logger.exception(e.message)
                continue

            try:
                business, establishment = IdentityBusinessApi.create_business(
                    **{
                        'individual_id': identity.pk,
                        'name': business_name
                    }
                )

                qrcode = Qrcode.objects.get(
                    owner=business
                )

            except Exception, e:
                logger.exception(e.message)
                continue

            try:
                endpoint_email = Endpoint.objects.create(
                    endpoint_type=EndpointTypes.EMAIL,
                    identity=establishment,
                    value=manager_email,
                    context='establishment_email',
                    primary=True,
                    validated=True
                )

            except Exception, e:
                logger.exception(e.message)
                continue

            if manager_phone:
                try:
                    endpoint_phone = Endpoint.objects.create(
                        endpoint_type=EndpointTypes.PHONE,
                        identity=establishment,
                        value=manager_phone,
                        context='establishment_phone',
                        primary=True,
                        validated=True
                    )

                except Exception, e:
                    logger.exception(e.message)
                    continue

            if business_website:
                try:
                    endpoint_website = Endpoint.objects.create(
                        endpoint_type=EndpointTypes.WEBSITE,
                        identity=establishment,
                        value=business_website,
                        context='establishment_website',
                        primary=True,
                        validated=True
                    )

                except Exception, e:
                    logger.exception(e.message)
                    continue

            if business_address:
                try:
                    endpoint_address = Endpoint.objects.create(
                        endpoint_type=EndpointTypes.ADDRESS,
                        identity=establishment,
                        value=business_address,
                        context='establishment_address',
                        primary=True,
                        validated=True
                    )

                except Exception, e:
                    logger.exception(e.message)
                    continue

            creation_counter += 1

            qrcode_url = ''.join([
                'http://chart.apis.google.com/chart',
                '?chs=280x280&cht=qr&chld=|1&chl=',
                urlquote_plus('/'.join([
                    settings.BASE_URL,
                    'qrcode',
                    qrcode.pk,
                    ''
                ]))
            ])

            logger.info(''.join([
                'Created User With: \n\t',
                'username: ',
                user.username,
                '\n\tindividual name: ',
                identity.name,
                '\n\tbusiness name: ',
                business.name,
                '\n\tbusiness email: ',
                endpoint_email.value,
                '\n\tbusiness phone: ',
                endpoint_phone.value,
                '\n\tbusiness website: ',
                endpoint_website.value,
                '\n\tbusiness address: ',
                endpoint_address.value,
                '\n\tqrcode: ',
                qrcode_url,
                '\n\n'
            ]))

            try:
                urllib.urlretrieve(
                    qrcode_url, ''.join([
                        './merchant-qrcodes/',
                        business.name,
                        '.png'
                    ])
                )

            except Exception, e:
                logger.exception(e.message)

        logger.info('Created %i Merchants' % (creation_counter,))
