from django.contrib.contenttypes.models import ContentType
from django.utils.log import getLogger
logger = getLogger(__name__)

from knotis.contrib.quick.models import QuickModel
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickIPAddressField,
    QuickForeignKey,
    QuickGenericForeignKey,
    QuickIntegerField,
)

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.models import Identity
from knotis.utils.regex import REGEX_CC_ANY
import re


class ApplicationTypes:
    KNOTIS_WEB = 'knotisweb'
    KNOTIS_MOBILE = 'knotismobile'

    CHOICES = (
        (KNOTIS_WEB, 'Knotis Web'),
        (KNOTIS_MOBILE, 'Knotis Mobile')
    )


class ActivityTypes:
    UNDEFINED = -1
    REQUEST = 0
    LOGIN = 1
    LOGOUT = 2
    SIGN_UP = 3
    PURCHASE = 4
    REDEEM = 5
    PROMO_CODE = 6
    CONNECT_RANDOM_COLLECTION = 7

    CHOICES = (
        (REQUEST, 'Request'),
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
        (SIGN_UP, 'Sign_up'),
        (PURCHASE, 'Purchase'),
        (REDEEM, 'Redeem'),
        (PROMO_CODE, 'Promo Code'),
        (CONNECT_RANDOM_COLLECTION, 'Connect a Random Offer Collection'),
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

    identity = QuickForeignKey(
        Identity,
        null=True,
        default=None
    )

    activity_type = QuickIntegerField(
        choices=ActivityTypes.CHOICES,
        default=ActivityTypes.UNDEFINED,
        db_index=True,
        blank=False
    )

    application = QuickCharField(
        null=True,
        max_length=64,
        choices=ApplicationTypes.CHOICES,
        db_index=True
    )

    context = QuickCharField(
        null=True,
        default=None,
        max_length=1024
    )

    url_path = QuickCharField(
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

    @classmethod
    def create_activity(cls, request, activity_type):
        if request.user.is_authenticated():
            try:
                authenticated_user = KnotisUser.objects.get(
                    pk=request.user.id
                )

            except:
                authenticated_user = None
                logger.exception('failed to get knotis user')

        else:
            authenticated_user = None

        try:
            cls.objects.create(
                ip_address=request.META.get('REMOTE_ADDR', None),
                authenticated_user=authenticated_user,
                activity_type=activity_type,
                application=ApplicationTypes.KNOTIS_WEB,
                context=clean_request_body(request),
                url_path=request.path,
            )
        except:
            logger.exception('failed to log web request activity')

    @classmethod
    def sign_up(cls, request):
        cls.create_activity(request, ActivityTypes.SIGN_UP)

    @classmethod
    def login(cls, request):
        cls.create_activity(request, ActivityTypes.LOGIN)

    @classmethod
    def logout(cls, request):
        cls.create_activity(request, ActivityTypes.LOGOUT)

    @classmethod
    def purchase(cls, request):
        cls.create_activity(request, ActivityTypes.PURCHASE)

    @classmethod
    def redeem(cls, request):
        cls.create_activity(request, ActivityTypes.REDEEM)


def clean_request_body(request):
    """
    This method should strip out credit card numbers
    and passwords and any other sensitive information
    from the request body so that it's suitable for
    logging.
    """

    body = request.body

    # redact credit card numbers
    body = re.sub(
        ''.join(['/b', REGEX_CC_ANY, '/b']),
        '<!-- REDACTED -->',
        body
    )
    return body


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
