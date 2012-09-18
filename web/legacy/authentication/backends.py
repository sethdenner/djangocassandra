from knotis_auth.models import User

class LegacyAuthenticationBackend(object):
    def authenticate(
        self,
        username=None,
        password=None
    ):
        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            return None
                
        if not user.check_pasword(password):
            return None
        
        user.set_password(password)
        user.save()
        return user
            
    def get_user(
        self,
        user_id
    ):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        