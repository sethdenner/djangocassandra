

from knotis.contrib.activity.models import (
    Activity,
    ActivityTypes,
)


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
        Activity.create_activity(
            request,
            ActivityTypes.REQUEST,
        )

        return None
