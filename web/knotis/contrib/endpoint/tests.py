from django.test import TestCase
from django.contrib.auth import authenticate

from knotis.contrib.identity.tests import IdentityModelTests
from knotis.contrib.auth.tests import UserCreationTests

from models import (
    EndpointEmail,
    EndpointTypes
)


class EndpointTests(TestCase):
    @staticmethod
    def create_test_endpoint(**kwargs):
        if not kwargs.get('identity'):
            kwargs['identity'] = IdentityModelTests.create_test_individual()

        if not kwargs.get('value'):
            kwargs['value'] = 'test@example.com'

        return EndpointEmail.objects.create(**kwargs)

    def test_create(self):
        endpoint = EndpointTests.create_test_endpoint()
        self.assertIsNotNone(endpoint)


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        self.user, self.user_identity = UserCreationTests.create_test_user()

    def test_endpoint_validation(self):
        endpoint = EndpointTests.create_test_endpoint(
            endpoint_type=EndpointTypes.EMAIL,
            value=self.user.username,
            identity=self.user_identity
        )

        # Attempt authentication.
        authenticated_user = authenticate(
            user_id=self.user.id,
            validation_key=endpoint.validation_key
        )

        self.assertNotEqual(
            authenticated_user,
            None,
            'Authentication Failed'
        )

        validated_endpoint = Endpoint.objects.get(pk=endpoint.id)

        self.assertEqual(
            validated_endpoint.validated,
            True,
            'Endpoint Was Not Validated'
        )

        # Make sure the same credentials don't auth again.
        authenticated_user = authenticate(
            user_id=self.user.id,
            validation_key=endpoint.validation_key
        )

        self.assertEqual(
            authenticated_user,
            None,
            'Validation Credentials Did Not Expire.'
        )
