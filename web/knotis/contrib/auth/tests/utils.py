
from knotis.contrib.auth.api import (
    AuthenticationApi
)
import random
from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.models import IdentityIndividual


class UserCreationTestUtils(object):

    @staticmethod
    def create_test_user(**kwargs):
        unique = str(random.randint(0, 100000))
        if not kwargs.get('first_name'):
            kwargs['first_name'] = 'John ' + unique

        if not kwargs.get('last_name'):
            kwargs['last_name'] = 'Doe' + unique

        if not kwargs.get('email'):
            kwargs['email'] = 'test_user' + unique + '@example.com'

        if not kwargs.get('password'):
            kwargs['password'] = 'test_password' + unique

        if not kwargs.get('name'):
            kwargs['name'] = kwargs['first_name'] + ' ' + kwargs['last_name']

        users = KnotisUser.objects.filter(username=kwargs.get('email'))
        if len(users):
            user = users[0]
            identity = IdentityIndividual.objects.get_individual(user)

        else:
            user, identity, errors = AuthenticationApi.create_user(
                send_validation=False,
                **kwargs
            )

        return user, identity
