import re

from knotis.contrib.activity.models import (
    Activity,
    ActivityTypes,
    ApplicationTypes
)
from knotis.contrib.auth.models import KnotisUser
from knotis.utils.regex import REGEX_CC_ANY

from django.utils.log import getLogger
logger = getLogger(__name__)


def clean_request_body(request):
    """
    This method should strip out credit card numbers
    and passwords and any other sensitive information
    from the request body so that it's suitable for
    logging.
    """
    body = request.read()

    # redact credit card numbers
    body = re.sub(
        ''.join(['/b', REGEX_CC_ANY, '/b']),
        '<!-- REDACTED -->',
        body
    )
    return body


class ActivityMiddleware(object):
    """
    Activity monitoring middleware.

    Right now it only monitors http requests.

    Should be placed after the Django Authentication
    middleware as it attempts to log the currently
    authenticated user.
    """
    def process_request(
        self,
        request
    ):
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
            Activity.objects.create(
                ip_address=request.META.get('REMOTE_ADDR', None),
                authenticated_user=authenticated_user,
                activity_type=ActivityTypes.REQUEST,
                application=ApplicationTypes.KNOTIS_WEB,
                message='web request recieved',
                context=clean_request_body(request)
            )

        except:
            logger.exception('failed to log web request activity')

        return None
