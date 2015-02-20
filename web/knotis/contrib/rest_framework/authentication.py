from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.models import AnonymousUser

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from doac.models import Client


class ClientOnlyAuthentication(BaseAuthentication):
    def authenticate(
        self,
        request
    ):
        client_id = request.DATA.get('client_id')
        if None is client_id:
            raise AuthenticationFailed(
                'No credentials provided.'
            )

        try:
            client = Client.objects.get(pk=client_id)

        except Exception, e:
            logger.exception(e.message)
            raise AuthenticationFailed(
                'No client could be found for these credentials.'
            )

        return AnonymousUser(), client
