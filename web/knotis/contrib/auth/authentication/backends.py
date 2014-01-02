from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.auth.models import KnotisUser


class CaseInsensitiveUsernameAuthenticationBackend(object):
    def authenticate(
        self,
        username=None,
        password=None
    ):
        try:
            user = KnotisUser.objects.get(username=username.lower())

        except:
            logger.exception('failed to retrive user')
            return None

        if not user.check_password(password):
            return None

        return user

    def get_user(
        self,
        user_id
    ):
        try:
            return KnotisUser.objects.get(pk=user_id)

        except:
            logger.exception('failed to retrieve user')
            return None
