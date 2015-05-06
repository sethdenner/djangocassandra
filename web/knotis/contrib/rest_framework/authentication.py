from django.utils.log import logging
logger = logging.getLogger(__name__)

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from oauth2_provider.models import Application


class ClientOnlyAuthentication(BaseAuthentication):
    def authenticate(
        self,
        request
    ):
        client_id = request.DATA.get(
            'client_id',
            request.QUERY_PARAMS.get('client_id')
        )

        if None is client_id:
            raise AuthenticationFailed(
                'No credentials provided.'
            )

        try:
            client = Application.objects.get(client_id=client_id)

        except Exception, e:
            logger.exception(e.message)
            raise AuthenticationFailed(
                'No client could be found for these credentials.'
            )

        try:
            user = client.user

        except Exception, e:
            logger.exception(e.message)
            raise AuthenticationFailed(
                'No user is associated with this client'
            )

        return user, client
