from sorl.thumbnail import ImageField
from knotis.contrib.sickle import generate_sorl_crop_string as crop

from knotis.contrib.quick.models import QuickModel

from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickFloatField,
    QuickForeignKey
)
from knotis.contrib.identity.models import Identity


class Image(QuickModel):
    owner = QuickForeignKey(Identity)
    image = ImageField(
        upload_to='images/',
        height_field='height',
        width_field='width'
    )
    width = QuickFloatField()
    height = QuickFloatField()

    def crop(
        self,
        left,
        top,
        width,
        height
    ):
        return crop(
            left,
            top,
            width,
            height
        )


class ImageInstance(QuickModel):
    owner = QuickForeignKey(Identity)
    image = QuickForeignKey(Image)
    related_object_id = QuickCharField(
        max_length=36,
        db_index=True
    )

    context = QuickCharField(
        max_length=16,
        db_index=True
    )

    crop_left = QuickFloatField()
    crop_top = QuickFloatField()
    crop_width = QuickFloatField()
    crop_height = QuickFloatField()

    def aspect_ratio(self):
        if self.crop_width and self.crop_height:
            return self.crop_width / self.crop_height

        else:
            return self.image.width / self.image.height

    def crop(self):
        return self.image.crop(
            self.crop_left,
            self.crop_top,
            self.crop_width,
            self.crop_height,
        )
