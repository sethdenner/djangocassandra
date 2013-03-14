import math

from django.db.models import (
    CharField,
    FloatField,
    Manager
)
from django.contrib.auth.models import User
from sorl.thumbnail import ImageField

from knotis.contrib.core.models import KnotisModel
from knotis.contrib.content.models import Content
from knotis.contrib.cassandra.models import ForeignKey


class ImageManager(Manager):
    def create_image(
        self,
        user,
        image,
        caption=None,
        related_object_id=None
    ):
        content_caption = None
        if None != caption:
            content_caption = Content(
                content_type='9.1',
                user=user,
                name='image_caption',
                value=caption
            )
            content_caption.save()

        image = Image.objects.create(
            user=user,
            image=image,
            caption=content_caption,
            related_object_id=related_object_id
        )

        return image


class Image(KnotisModel):
    user = ForeignKey(User)
    related_object_id = CharField(
        max_length=36,
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    image = ImageField(upload_to='images/')
    caption = ForeignKey(
        Content,
        related_name='image_caption',
        default=None,
        null=True,
        blank=True
    )
    crop_left = FloatField(
        null=True,
        blank=True,
        default=None
    )
    crop_top = FloatField(
        null=True,
        blank=True,
        default=None
    )
    crop_right = FloatField(
        null=True,
        blank=True,
        default=None
    )
    crop_bottom = FloatField(
        null=True,
        blank=True,
        default=None
    )
    crop_width = FloatField(
        null=True,
        blank=True,
        default=None
    )
    crop_height = FloatField(
        null=True,
        blank=True,
        default=None
    )

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

    def update(
        self,
        image=None,
        caption=None
    ):
        is_self_dirty = False
        if None != image and image != self.image:
            image = image
            is_self_dirty = True

        if None != caption and caption != self.caption.value:
            self.caption.value = caption
            self.caption.save()

        if is_self_dirty:
            self.save()

    objects = ImageManager()
