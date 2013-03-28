import urllib

from django.test import TestCase
from django.core.files import File

from knotis.contrib.identity.tests import IdentityModelTests

from knotis.contrib.media.models import Image


class MediaTests(TestCase):
    @staticmethod
    def create_test_image(**kwargs):
        if not kwargs.get('owner'):
            kwargs['owner'] = IdentityModelTests.create_test_individual()

        if not kwargs.get('related_object_id'):
            kwargs['related_object_id'] = kwargs['owner'].id

        if not kwargs.get('image'):
            response = urllib.urlretrieve('http://placehold.it/1x1')
            kwargs['image'] = File(open(response[0]))

        if not kwargs.get('caption'):
            kwargs['caption'] = 'Test image caption'

        return Image.objects.create(**kwargs)

    def test_image_create(self):
        image = MediaTests.create_test_image()
        self.assertIsNotNone(image)
