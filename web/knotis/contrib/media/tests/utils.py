import urllib

from knotis.contrib.auth.tests.utils import UserCreationTestUtils

from knotis.contrib.media.api import (
    ImageApi,
    ImageInstanceApi
)


class MediaTestUtils(object):
    @staticmethod
    def create_test_image(**kwargs):
        if not kwargs.get('owner'):
            _, kwargs['owner'] = UserCreationTestUtils.create_test_user()

        if not kwargs.get('related_object_id'):
            kwargs['related_object_id'] = kwargs['owner'].id

        if not kwargs.get('image'):
            response = urllib.urlretrieve('http://placehold.it/1x1')
            kwargs['image'] = response[0]

        if not kwargs.get('caption'):
            kwargs['caption'] = 'Test image caption'

        image = ImageApi.import_image(kwargs['image'], kwargs['owner'])
        image_instance = ImageInstanceApi.create_image_instance(
            image=image,
            owner=kwargs['owner'],
        )

        return image_instance
