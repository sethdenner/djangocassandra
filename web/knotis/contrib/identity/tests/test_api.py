from unittest import TestCase

from rest_framework.test import APIClient
# from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from oauth2_provider.models import Application


class IdentityApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_password = 'test_password'
        self.client_id = Application.objects.filter(
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD
        )[0]

    def test_establishment_api(self):

        response = self.client.get(
            '/api/v0/identity/establishment/?page=1&client_id=%s' % (
                self.client_id
            )
        )
        self.assertEqual(response.status_code, 200)
