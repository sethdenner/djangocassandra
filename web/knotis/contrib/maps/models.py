from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.contenttypes.models import ContentType

from knotis.contrib.quick.models import QuickModel
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickFloatField,
    QuickForeignKey,
    QuickUUIDField,
    QuickGenericForeignKey
)


class Location(QuickModel):
    id = QuickCharField(
        primary_key=True,
        max_length='20',
        required=False
    )
    address = QuickCharField(max_length=256)
    latitude = QuickFloatField()
    longitude = QuickFloatField()

    @staticmethod
    def generate_id(
        latitude,
        longitude
    ):
        def format_coordinate(coordinate):
            return '%011.7f' % coordinate

        return ''.join([
            format_coordinate(latitude + 90.),
            format_coordinate(longitude + 180.)
        ]).replace('.', '')

    def save(
        self,
        related=None,
        *args,
        **kwargs
    ):
        create = not self.id
        if create:
            self.id = Location.generate_id(
                self.latitude,
                self.longitude
            )

        super(Location, self).save(
            *args,
            **kwargs
        )

        if create:
            if related:
                try:
                    LocationItem.objects.create(
                        location=self,
                        related=related
                    )

                except Exception:
                    logger.exception('Failed to create location item')

                    """
                    don't clean up locations.
                    primary keys will always resolve right.
                    """
                    raise


class LocationItem(QuickModel):
    location = QuickForeignKey(Location)
    related_content_type = QuickForeignKey(
        ContentType,
        related_name='locationitem_related_set'
    )
    related_objects_id = QuickUUIDField()
    related = QuickGenericForeignKey(
        'related_content_type',
        'related_object_id'
    )
