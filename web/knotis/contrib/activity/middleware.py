

from knotis.contrib.activity.models import (
    Activity,
    ActivityTypes,
)
import settings


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
        if not (
            request.path.startswith(settings.MEDIA_URL) or
            request.path.startswith(settings.STATIC_URL)
        ):
            Activity.create_activity(
                request,
                ActivityTypes.REQUEST,
            )

        return None
