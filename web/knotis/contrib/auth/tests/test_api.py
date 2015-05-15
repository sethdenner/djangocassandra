from unittest import TestCase

from rest_framework.test import APIClient
from knotis.contrib.auth.tests.utils import UserCreationTestUtils


class AuthValidationView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_password = 'test_password'
        self.user, self.user_identity = UserCreationTestUtils.create_test_user(
            password=self.user_password
        )
        self.client.login(
            username=self.user.username,
            password=self.user_password
        )
