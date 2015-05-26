import re

from django.utils import log
logger = log.getLogger(__name__)

from django.http import HttpResponseRedirect

from knotis.contrib.auth.models import UserInformation


class MobileAppRedirectMiddleware(object):
    """
    This middleware detects if the user has installed the
    mobile app or not. If so and they are visiting the
    web application with a mobile user agent string then the
    user will be redirected to the mobile app.
    """

    def process_request(
        self,
        request
    ):
        if not request.user.is_authenticated():
            return

        try:
            user_information = UserInformation.objects.get(
                user=request.user
            )

        except Exception, e:
            logger.exception(e.message)
            return

        if not user_information.mobile_app_installed:
            return

        if not request.user_agent.is_mobile:
            return

        return HttpResponseRedirect(
            '/'.join([
                'knotis:/',
                request.get_full_path()
            ])
        )
