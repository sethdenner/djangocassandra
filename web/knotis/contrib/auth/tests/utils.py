
from knotis.contrib.auth.api import (
    AuthenticationApi
)
import random


class UserCreationTestUtils(object):

    @staticmethod
    def create_test_user(**kwargs):
        unique = str(random.randint(0, 100000))
        if not kwargs.get('first_name'):
            kwargs['first_name'] = 'Test' + unique

        if not kwargs.get('last_name'):
            kwargs['last_name'] = 'User' + unique

        if not kwargs.get('email'):
            kwargs['email'] = 'test_user' + unique + '@example.com'

        if not kwargs.get('password'):
            kwargs['password'] = 'test_password' + unique

        user, identity, errors = AuthenticationApi.create_user(
            send_validation=False,
            **kwargs
        )
        return user, identity
