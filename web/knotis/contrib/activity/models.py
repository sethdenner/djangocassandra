from django.contrib.contenttypes.models import ContentType
from django.utils.log import getLogger
logger = getLogger(__name__)

from knotis.contrib.quick.models import QuickModel
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickIPAddressField,
    QuickForeignKey,
    QuickGenericForeignKey
)
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


class Activity(QuickModel):
    ip_address = QuickIPAddressField(
        null=True,
        default=None,
        db_index=True
    )
    authenticated_user = QuickForeignKey(
        KnotisUser,
        null=True,
        default=None
    )

    activity_type = QuickCharField(
        null=True,
        max_length=64,
        choices=ActivityTypes.CHOICES,
        db_index=True
    )

    application = QuickCharField(
        null=True,
        max_length=64,
        choices=ApplicationTypes.CHOICES,
        db_index=True
    )

    message = QuickCharField(
        null=True,
        default=None,
        max_length=1024
    )

    context = QuickCharField(
        null=True,
        default=None,
        max_length=1024
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
                        related=obj
                    )

                except:
                    logger.exception(
                        'failed to create activity object relation'
                    )


class ActivityRelation(QuickModel):
    activity = QuickForeignKey(Activity)

    related_content_type = QuickForeignKey(
        ContentType,
        related_name='activity_activityrelation_related_content_types'
    )
    related_object_id = QuickCharField(max_length=32)
    related = QuickGenericForeignKey(
        'related_content_type',
        'related_object_id'
    )
