
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

from geopy.geocoders import Nominatim

from django.conf import settings


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
        if self.longitude is not None and self.latitude is not None:
            return Point(self.longitude, self.latitude)

        else:
            return None

    def update_geocode(self):
        if not self.latitude or not self.longitude:
            geocoder = Nominatim(domain=settings.NOMINATIM_API)
            # This is how one changes the api server.  Found by looking at
            # geopy source:
            # https://github.com/geopy/geopy/blob/master/geopy/geocoders/osm.py#L48
            location = geocoder.geocode(
                self.address,
                exactly_one=True
            )

            address, (self.latitude, self.longitude) = location

        return self


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
