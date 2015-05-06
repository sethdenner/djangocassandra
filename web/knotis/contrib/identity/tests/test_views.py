
from unittest import TestCase
from django.test import Client


from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from knotis.contrib.identity.models import Identity
from knotis.contrib.auth.emails import get_validation_url


class IdentityViewTests(TestCase):
    def setUp(self):
        self.user_password = 'test_password'
        self.user, self.user_identity = UserCreationTestUtils.create_test_user(
            password=self.user_password
        )
        self.client = Client()
        login_args = {
            'username': self.user.username,
            'password': self.user_password
        }
        self.client.post('/login/', login_args)

    def test_identity_switcher_view(self):
        available_identities = Identity.objects.get_available(
            user=self.user
        )
        for x in available_identities:
            response = self.client.get('/identity/switcher/%s/' % x.id)
            self.assertEqual(response.status_code, 302)
