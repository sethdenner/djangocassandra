from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point

from polymodels.utils import get_content_type

from knotis.contrib.quick.models import QuickModel
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickFloatField,
    QuickForeignKey,
    QuickUUIDField,
    QuickGenericForeignKey
)


class Location(QuickModel):
    address = QuickCharField(max_length=256)
    latitude = QuickFloatField()
    longitude = QuickFloatField()

    def save(
        self,
        *args,
        **kwargs
    ):
        content_type = get_content_type(self.__class__, self._state.db)
        setattr(self, self.CONTENT_TYPE_FIELD, content_type)

        super(Location, self).save(
            *args,
            **kwargs
        )

    def get_location(self):
        return Point(self.longitude, self.latitude)


class LocationItem(QuickModel):
    location = QuickForeignKey(Location)
    related_content_type = QuickForeignKey(
        ContentType,
        related_name='locationitem_related_set',
    )
    related_object_id = QuickUUIDField(
        db_index=True
    )
    related = QuickGenericForeignKey(
        'related_content_type',
        'related_object_id'
    )
