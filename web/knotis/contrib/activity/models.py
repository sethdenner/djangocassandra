from django.db.models import (
    CharField,
    IPAddressField,
    DateTimeField,
    ForeignKey
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.utils.log import getLogger
logger = getLogger(__name__)

from knotis.contrib.core.models import KnotisModel
from knotis.contrib.auth.models import KnotisUser


class ApplicationTypes:
    KNOTIS_WEB = 'knotisweb'
    KNOTIS_MOBILE = 'knotismobile'

    CHOICES = (
        (KNOTIS_WEB, 'Knotis Web'),
        (KNOTIS_MOBILE, 'Knotis Mobile')
    )


class ActivityTypes:
    REQUEST = 'request'
    LOGIN = 'login'
    REGISTRATION = 'registration'
    PURCHASE = 'purchase'
    CLICK = 'click'

    CHOICES = (
        (REQUEST, 'Request'),
        (LOGIN, 'Login'),
        (REGISTRATION, 'Registration'),
        (PURCHASE, 'Purchase'),
        (CLICK, 'Click')
    )


class Activity(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Activity"
        verbose_name_plural = "Activity"

    ip_address = IPAddressField(
        null=True,
        default=None,
        db_index=True
    )
    authenticated_user = ForeignKey(
        KnotisUser,
        null=True,
        default=None
    )

    activity_type = CharField(
        null=True,
        max_length=64,
        choices=ActivityTypes.CHOICES,
        db_index=True
    )

    application = CharField(
        null=True,
        max_length=64,
        choices=ApplicationTypes.CHOICES,
        db_index=True
    )

    message = CharField(
        null=True,
        default=None,
        max_length=1024
    )

    context = CharField(
        null=True,
        default=None,
        max_length=1024
    )

    pub_date = DateTimeField(
        null=True,
        auto_now_add=True
    )

    def save(
        self,
        related=None,
        *args,
        **kwargs
    ):
        activity = super(Activity, self).save(*args, **kwargs)

        if related and len(related):
            for obj in related:
                try:
                    ActivityRelation.objects.create(
                        activity=activity,
                        content_object=obj
                    )

                except:
                    logger.exception(
                        'failed to create activity object relation'
                    )


class ActivityRelation(KnotisModel):
    activity = ForeignKey(Activity)

    content_type = ForeignKey(ContentType)
    object_id = CharField(max_length=32)
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )
