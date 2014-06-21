from django.conf import settings
from django.utils import log
logger = log.getLogger(__name__)

from sorl.thumbnail import (
    ImageField,
    get_thumbnail
)
from knotis.contrib.sickle import generate_sorl_crop_string as crop

from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)

from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickFloatField,
    QuickForeignKey,
    QuickBooleanField
)


class Image(QuickModel):
    owner = QuickForeignKey('identity.Identity')
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


class ImageInstanceManager(QuickManager):
    def create(
        self,
        *args,
        **kwargs
    ):
        super(ImageInstanceManager, self).create(
            *args,
            **kwargs
        )


class ImageInstance(QuickModel):
    owner = QuickForeignKey('identity.Identity')
    image = QuickForeignKey(Image)
    related_object_id = QuickCharField(
        max_length=36,
        db_index=True
    )

    context = QuickCharField(
        max_length=50,
        db_index=True
    )

    primary = QuickBooleanField(
        db_index=True,
        default=False
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

    def cropped_url(self):
        thumb = get_thumbnail(
            self.image.image,
            'x'.join([
                str(int(self.crop_width)),
                str(int(self.crop_height))
            ]),
            crop=self.crop()
        )
        return settings.BASE_URL + thumb.url

    def save(self, *args, **kwargs):
        super(ImageInstance, self).save(*args, **kwargs)

        if self.primary:
            other_instances = ImageInstance.objects.filter(
                related_object_id=self.related_object_id,
                primary=True,
                context=self.context
            )

            for i in other_instances:
                if i.id != self.id:
                    i.primary = False
                    i.save()
