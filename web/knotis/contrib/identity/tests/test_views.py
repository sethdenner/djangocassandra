
from unittest import TestCase


from knotis.contrib.auth.tests.utils import UserCreationTestUtils


class IdentityViewTests(TestCase):
    def setUp(self):
        self.user_password = 'test_password'
        self.user, self.user_identity = UserCreationTestUtils.create_test_user(
            password=self.user_password
        )

    def test_identity_switcher_view(self):
        self.client.login(
            username=self.user.username,
            password=self.user_password
        )
        response = self.client.get('/identity/switcher/')
        self.assertEqual(response.status_code, 200)

    # Commenting this because I want to get it working but not now.
    def test_primary_image(self):
        pass
