import urllib

from knotis.contrib.auth.tests.utils import UserCreationTestUtils

from knotis.contrib.media.api import (
    ImageApi,
    ImageInstanceApi
)
import random
import time


class MediaTestUtils(object):
    @staticmethod
    def create_test_image(**kwargs):
        if not kwargs.get('owner'):
            _, kwargs['owner'] = UserCreationTestUtils.create_test_user()

        if not kwargs.get('related_object_id'):
            kwargs['related_object_id'] = kwargs['owner'].id

        if not kwargs.get('caption'):
            kwargs['caption'] = 'Test image caption'

        if not kwargs.get('context'):
            kwargs['context'] = 'offer_banner'

        if not kwargs.get('image'):
            # response = urllib.urlretrieve('http://placehold.it/350x150')
            for x in xrange(3):
                size_x = str(random.randint(200, 600))
                size_y = str(random.randint(200, 600))
                url = 'http://placekitten.com/g/' + size_x + '/' + size_y
                response = urllib.urlretrieve(url)
                image_path = response[0]
                image_has_data = open(image_path).read() != ''

            if not image_has_data:
                time.sleep(3)
                url = 'http://placehold.it/350x150'
                # url = 'http://placekitten.com/g/200/300'
                response = urllib.urlretrieve(url)
                image_path = response[0]

            kwargs['image'] = response[0]

        image = ImageApi.import_image(kwargs['image'], kwargs['owner'])

        image_instance = ImageInstanceApi.create_image_instance(
            image=image,
            owner=kwargs['owner'],
            context=kwargs.get('context')
        )

        return image_instance
