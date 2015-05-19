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

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.auth.api import AuthenticationApi
from knotis.contrib.identity.models import (
    IdentityIndividual,
    IdentityBusiness
)
from knotis.contrib.identity.api import (
    IdentityApi,
)
from knotis.contrib.endpoint.models import (
    EndpointEmail,
    EndpointPhone,
    EndpointAddress,
    EndpointWebsite
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

            business_name = merchant_data.get(
                Columns.BUSINESS_NAME,
                ''
            ).strip()
            manager_name = merchant_data.get(
                Columns.MANAGER_NAME,
                ''
            ).strip()
            manager_email = merchant_data.get(
                Columns.MANAGER_EMAIL,
                ''
            ).strip()
            manager_phone = merchant_data.get(
                Columns.MANAGER_PHONE,
                ''
            ).strip()
            business_website = merchant_data.get(
                Columns.BUSINESS_WEBSITE,
                ''
            ).strip()
            business_address = merchant_data.get(
                Columns.BUSINESS_ADDRESS,
                ''
            ).strip()

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

            else:
                manager_email = manager_email.lower()

            if not manager_name:
                manager_name = manager_email.split('@')[0]

            try:
                user = KnotisUser.objects.get(username=manager_email)

            except KnotisUser.DoesNotExist:
                user = None

            except Exception, e:
                logger.exception(e.message)
                continue

            if user:
                try:
                    identity = IdentityIndividual.objects.get_individual(user)

                except Exception, e:
                    logger.exception(e.message)
                    continue

            else:
                try:
                    user, identity, errors = AuthenticationApi.create_user(**{
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

            business = None
            business_name_normalized = business_name.replace(' ', '').lower()
            existing_businesses = IdentityBusiness.objects.get_businesses(
                identity
            )
            for b in existing_businesses:
                if business_name_normalized == b.name.replace(' ', '').lower():
                    business = b
                    break

            if business:
                establishment = IdentityApi.create_establishment(
                    **{
                        'business_id': business.pk,
                        'name': business_name
                    }
                )

            else:
                try:
                    (
                        business,
                        establishment
                    ) = IdentityApi.create_business(
                        **{
                            'individual_id': identity.pk,
                            'name': business_name
                        }
                    )

                except Exception, e:
                    logger.exception(e.message)
                    continue

            try:
                qrcode = Qrcode.objects.get(
                    owner=establishment
                )

            except Exception, e:
                logger.exception(e.message)
                continue

            try:
                endpoint_email = EndpointEmail.objects.create(
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
                # Should probably use a regex but I'm too lazy to look it up
                manager_phone = manager_phone.replace(
                    '.',
                    ''
                ).replace(
                    '-',
                    ''
                ).replace(
                    '(',
                    ''
                ).replace(
                    ')',
                    ''
                ).replace(
                    ' ',
                    ''
                )

                try:
                    endpoint_phone = EndpointPhone.objects.create(
                        identity=establishment,
                        value=manager_phone,
                        context='establishment_phone',
                        primary=True,
                        validated=True
                    )

                except Exception, e:
                    logger.exception(e.message)
                    continue
            else:
                endpoint_phone = None

            if business_website:
                try:
                    endpoint_website = EndpointWebsite.objects.create(
                        identity=establishment,
                        value=business_website,
                        context='establishment_website',
                        primary=True,
                        validated=True
                    )

                except Exception, e:
                    logger.exception(e.message)
                    continue
            else:
                endpoint_website = None

            if business_address:
                try:
                    endpoint_address = EndpointAddress.objects.create(
                        identity=establishment,
                        value=business_address,
                        context='establishment_address',
                        primary=True,
                        validated=True
                    )

                except Exception, e:
                    logger.exception(e.message)
                    continue
            else:
                endpoint_address = None

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

            try:
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
                    endpoint_phone.value if endpoint_phone else '',
                    '\n\tbusiness website: ',
                    endpoint_website.value if endpoint_website else '',
                    '\n\tbusiness address: ',
                    endpoint_address.value if endpoint_address else '',
                    '\n\tqrcode: ',
                    qrcode_url,
                    '\n\n'
                ]))

            except UnicodeDecodeError, e:
                logger.exception(e.message)

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
