from django.db.models import (
    CharField, 
    IntegerField,
    Manager
)
from django.contrib.auth.models import User
from sorl.thumbnail import ImageField

from knotis.apps.core.models import KnotisModel
from knotis.apps.content.models import Content
from knotis.apps.cassandra.models import ForeignKey


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
    crop_left = IntegerField(
        null=True,
        blank=True,
        default=None
    )
    crop_top = IntegerField(
        null=True,
        blank=True,
        default=None
    )
    crop_right = IntegerField(
        null=True,
        blank=True,
        default=None
    )
    crop_bottom = IntegerField(
        null=True,
        blank=True,
        default=None
    )
    crop_width = IntegerField(
        null=True,
        blank=True,
        default=None
    )
    crop_height = IntegerField(
        null=True,
        blank=True,
        default=None
    )

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
