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
    address = QuickCharField(max_length=256)
    latitude = QuickFloatField()
    longitude = QuickFloatField()


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
