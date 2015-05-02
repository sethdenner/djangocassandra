import os

from unittest import TestCase

from knotis.contrib.auth.tests.utils import UserCreationTestUtils

# from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from rest_framework import status


class MediaTests(TestCase):
    def setUp(self):
        self.user, self.identity = UserCreationTestUtils.create_test_user(
            password='aoeu'
        )
        self.client = APIClient()
        self.client.login(username=self.user.username, password='aoeu')
        self.image_name = 'test_image.png'
        image_path = os.path.join(
            os.getenv('install_location'),
            'web/knotis/contrib/media/tests/',
            self.image_name
        )

        with open(image_path) as image:
            self.image_source = unicode(image.read(), 'ISO-8859-1')

    def test_image_upload(self):
        url = '/api/v0/media/imageinstance/'
        data = {
            'image': self.image_source,
            'name': self.image_name,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_no_image_exception(self):
        url = '/api/v0/media/imageinstance/'
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
