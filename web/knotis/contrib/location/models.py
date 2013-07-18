from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.contenttypes.models import ContentType

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
    id = QuickCharField(
        primary_key=True,
        required=False,
        max_length='20',
        default=None
    )
    address = QuickCharField(max_length=256)
    latitude = QuickFloatField()
    longitude = QuickFloatField()

    def __init__(
        self,
        *args,
        **kwargs
    ):
        self.force_insert = False

        super(Location, self).__init__(
            *args,
            **kwargs
        )

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

    def validate_unique(
        self,
        *args,
        **kwargs
    ):
        pass

    def clean(self):
        super(Location, self).clean()

        if not self.id:
            self.id = Location.generate_id(
                self.latitude,
                self.longitude
            )

        self.force_insert = False
        try:
            Location.objects.get(pk=self.id)

        except Location.DoesNotExist:
            self.force_insert = True

        except:
            pass

    def save(
        self,
        *args,
        **kwargs
    ):
        content_type = get_content_type(self.__class__, self._state.db)
        setattr(self, self.CONTENT_TYPE_FIELD, content_type)

        super(Location, self).save(
            force_insert=self.force_insert,
            *args,
            **kwargs
        )


class LocationItem(QuickModel):
    location = QuickForeignKey(Location)
    related_content_type = QuickForeignKey(
        ContentType,
        related_name='locationitem_related_set'
    )
    related_object_id = QuickUUIDField()
    related = QuickGenericForeignKey(
        'related_content_type',
        'related_object_id'
    )
