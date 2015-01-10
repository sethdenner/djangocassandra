
from django.test import TestCase

from .utils import MediaTestUtils


class MediaTests(TestCase):

    def test_image_create(self):
        image = MediaTestUtils.create_test_image()
        self.assertIsNotNone(image)
