import math

from sorl.thumbnail import ImageField

from knotis.contrib.quick.models import QuickModel

from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickFloatField,
    QuickForeignKey
)
from knotis.contrib.identity.models import Identity


class Image(QuickModel):
    owner = QuickForeignKey(Identity)
    related_object_id = QuickCharField(
        max_length=36,
        db_index=True
    )
    image = ImageField(upload_to='images/')

    caption = QuickCharField(max_length=140)

    crop_left = QuickFloatField()
    crop_top = QuickFloatField()
    crop_right = QuickFloatField()
    crop_bottom = QuickFloatField()
    crop_width = QuickFloatField()
    crop_height = QuickFloatField()

    def crop(self):
        if (
            self.crop_left and
            self.crop_top and
            self.crop_width and
            self.crop_height
        ):
            return ''.join([
                str(int(math.floor(self.crop_left))),
                'px ',
                str(int(math.floor(self.crop_top))),
                'px ',
                str(int(math.floor(self.crop_width))),
                'px ',
                str(int(math.floor(self.crop_height))),
                'px'
            ])

        else:
            return 'noop'
