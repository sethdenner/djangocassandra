from django.core.management.base import (
    BaseCommand,
    CommandError
)

from knotis.contrib.location.models import Location, LocationItem

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = 'Fill naked location fields with geocoder.'

    def handle(self, *args, **options):
        for location in Location.objects.all():
            if location.address and None in (
                    getattr(location, 'latitude'),
                    getattr(location, 'longitude')
            ):
                try:
                    location.update_geocode()
                    logger.info('Adding (%s, %s) to address %s' % (
                        location.address,
                        location.latitude,
                        location.longitude
                    ))

                except Exception:
                    logger.exception('Failed to geocode %s' % location.address)
                    continue

                try:
                    location.save()
                except Exception:
                    logger.exception('Failed to save location')
