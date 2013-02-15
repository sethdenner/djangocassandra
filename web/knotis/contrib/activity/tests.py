from django.test import TestCase

from knotis.contrib.activity.models import (
    Activity,
    ActivityTypes,
    ApplicationTypes
)

from knotis.contrib.auth.models import (
    KnotisUser
)


class ActivityTests(TestCase):
    def setUp(self):
        pass

    def test_request_activity_middleware(self):
        response = self.client.get('/')

        self.assertEqual(200, response.status_code)

        activity = Activity.objects.filter(
            activity_type=ActivityTypes.REQUEST,
            application=ApplicationTypes.KNOTIS_WEB
        )

        self.assertEqual(1, activity.count())

        # Clean up the activity we created
        activity[0].delete()

        # Create a user and log in to test authenticated
        # user logging

        test_username = 'test_user@totallyfaketestaccounts.com'
        test_password = 'test_password'
        test_user, _ = KnotisUser.objects.create_user(
            'test',
            'user',
            test_username,
            test_password
        )

        self.client.login(
            username=test_username,
            password=test_password
        )
        response = self.client.get('/')

        self.assertEqual(200, response.status_code)

        activity = Activity.objects.filter(
            activity_type=ActivityTypes.REQUEST,
            application=ApplicationTypes.KNOTIS_WEB,
            authenticated_user=test_user
        )

        self.assertEqual(1, activity.count())

        # Clean up user and activity
        test_user.delete()
        activity[0].delete()
