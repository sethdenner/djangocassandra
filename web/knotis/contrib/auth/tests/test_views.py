
from unittest import TestCase
from django.test import Client

from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from knotis.contrib.auth.emails import get_validation_url
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)


class AuthValidationView(TestCase):
    def setUp(self):
        self.user_password = 'test_password'
        self.user, self.user_identity = UserCreationTestUtils.create_test_user(
            password=self.user_password
        )
        self.client = Client()
        self.endpoint = Endpoint.objects.get(
            identity=self.user_identity,
            endpoint_type=EndpointTypes.EMAIL,
            primary=True,
        )

    def test_validation_link(self):
        link = get_validation_url(self.user, self.endpoint)

        response = self.client.get(link)
        self.assertEqual(response.status_code, 302)

    def test_login(self):
        login_args = {
            'username': self.user.username,
            'password': self.user_password
        }

        self.client.post('/login/', login_args)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
