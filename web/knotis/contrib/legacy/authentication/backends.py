from knotis.contrib.auth.models import KnotisUser


class LegacyAuthenticationBackend(object):
    def authenticate(
        self,
        username=None,
        password=None
    ):
        try:
            user = KnotisUser.objects.get(username=username)

        except KnotisUser.DoesNotExist:
            return None

        if not user.check_password(password):
            return None

        user.set_password(password)
        user.save()
        return user

    def get_user(
        self,
        user_id
    ):
        try:
            return KnotisUser.objects.get(pk=user_id)
        except KnotisUser.DoesNotExist:
            return None
