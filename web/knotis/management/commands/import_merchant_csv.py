import csv

from django.utils import log
logger = log.getLogger(__name__)

from django.core.management.base import (
    BaseCommand,
    CommandError
)

from knotis.contrib.auth.api import AuthUserApi


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

        for row in csv_reader:
            column_index = 0
            merchant_data = {}

            for column in row:
                merchant_data[
                    column_map[column_index]
                ] = column

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
                manager_email = DEFAULT_EMAIL_TEMPLATE % business_name.strip(
                    ' '
                ).lower()

            try:
                user, identity, errors = AuthUserApi.create_user(**{
                    'email': manager_email,
                    'password': 'asdfj89f3'
                })

            except Exception, e:
                logger.exception(e.message)
                continue

            identity.name = manager_name
            identity.save()

            business = IdentityBusiness.objects.
