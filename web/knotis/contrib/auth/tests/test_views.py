
from unittest import TestCase
from django.test import Client

from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from knotis.contrib.auth.emails import get_validation_url
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
import random


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


class NewUserView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_double_signup(self):
        user_password = 'test_password'
        user_name = 'sebastian+test_%s@knotis.com' % random.random()
        login_dict = {
            'email': user_name,
            'password': user_password,
            'format': 'json'
        }

        first_response = self.client.post('/signup/', login_dict)
        self.assertEqual(first_response.status_code, 200)

        second_response = self.client.post('/signup/', login_dict)
        self.assertEquals(
            second_response.content,
            ''.join([
                '{',
                '"message": "An error occurred during account creation", ',
                '"errors": {"email": ["Email address is already in use."]}, ',
                '"modal": true}'
            ])
        )
