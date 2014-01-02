from knotis.contrib.auth.models import KnotisUser


class HamburgertimeAuthenticationBackend(object):
    '''
    This is a terrible solution to the problem of needing management to be
    able to edit merchants information.

    This should be replaced with a proper admin too ASAP!

    If you are reading this message please contact your manager IMMEDIATELY
    and DEMAND to know why the fuck this is still live in production.

    Thanks,

    Seth Denner
    10/04/2012
    '''
    HAMBURGERTIME_USERNAME = '__hamburgertime__'

    def authenticate(
        self,
        username=None,
        password=None
    ):
        try:
            hamburgertime = KnotisUser.objects.get(
                username=self.HAMBURGERTIME_USERNAME
            )

        except:
            hamburgertime = None

        if None == hamburgertime:
            return None

        if not hamburgertime.check_password(password):
            return None

        try:
            user = KnotisUser.objects.get(username=username)
        except:
            user = None

        return user

    def get_user(
        self,
        user_id
    ):
        try:
            return KnotisUser.objects.get(pk=user_id)
        except:
            return None


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
