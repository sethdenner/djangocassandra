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

        except Exception, e:
            logger.exception('failed to retrieve user: %s' % e.message)
            return None
        try:
            if not user.check_password(password):
                return None

        except Exception, e:
            logger.error('Failed to check password! %s' % e.message)
            return None

        return user

    def get_user(
        self,
        user_id
    ):
        try:
            return KnotisUser.objects.get(pk=user_id)

        except Exception, e:
            logger.exception('failed to retrieve user: %s' % e.message)
            return None
