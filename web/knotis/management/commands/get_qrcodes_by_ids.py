import csv
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

from knotis.contrib.identity.models import (
    Identity,
    IdentityBusiness,
    IdentityTypes
)
from knotis.contrib.qrcode.models import Qrcode


class Command(BaseCommand):
    args = '<csv_file>'
    help = (
        'Gets the qrcodes belonging to the business/establishment IDs provided'
        '<id_1>,<id_2>,...,<id_n>'
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

        for row in csv_reader:
            for column in row:
                try:
                    identity = Identity.objects.get(pk=column)

                except Exception, e:
                    logger.exception(e.message)
                    continue

                if identity.identity_type == IdentityTypes.ESTABLISHMENT:
                    try:
                        identity = (
                            IdentityBusiness.objects.get_establishment_parent(
                                identity
                            )
                        )

                    except Exception, e:
                        logger.exception(e.message)
                        continue

                if not identity.identity_type == IdentityTypes.BUSINESS:
                    logger.error(
                        'Can only get QRCodes for '
                        'Establishment and Business IDS'
                    )
                    continue

                try:
                    qrcode = Qrcode.objects.get(
                        owner=identity
                    )

                except Exception, e:
                    logger.exception(e.message)
                    continue

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
                    urllib.urlretrieve(
                        qrcode_url, ''.join([
                            './merchant-qrcodes/',
                            identity.name,
                            '.png'
                        ])
                    )
                    logger.info(
                        'Created QRCode: %s for %s' % (
                            qrcode_url,
                            identity.name
                        )
                    )

                except Exception, e:
                    logger.exception(e.message)
