from django.test import TestCase

from knotis.contrib.identity.tests import IdentityModelTests

from models import (
    Endpoint,
    EndpointTypes
)


class EndpointTests(TestCase):
    @staticmethod
    def create_test_endpoint(**kwargs):
        if not kwargs.get('endpoint_type'):
            kwargs['endpoint_type'] = EndpointTypes.EMAIL

        if not kwargs.get('identity'):
            kwargs['identity'] = IdentityModelTests.create_test_individual()

        if not kwargs.get('value'):
            kwargs['value'] = 'test@example.com'

        return Endpoint.objects.create(**kwargs)

    def test_create(self):
        endpoint = EndpointTests.create_test_endpoint()
        self.assertIsNotNone(endpoint)
