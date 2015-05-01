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

        if not kwargs.get('caption'):
            kwargs['caption'] = 'Test image caption'

        if not kwargs.get('context'):
            kwargs['context'] = 'offer_banner'

        if not kwargs.get('image'):

            if kwargs['context'] == 'profile_badge':
                size_y = size_x = 80

            if kwargs['context'] == 'offer_banner':
                size_x = 339
                size_y = 199

            if kwargs['context'] == 'profile_banner':
                size_x = 2555
                size_y = 500

            url = 'http://placehold.it/' + str(size_x) + 'x' + str(size_y)

            # url = 'http://placehold.it/350/150'
            # url = 'http://placekitten.com/g/200/300'
            response = urllib.urlretrieve(url)

            kwargs['image'] = response[0]

        image = ImageApi.import_image_from_path(
            kwargs['image'],
            kwargs['owner'],
        )

        image_instance = ImageInstanceApi.create_image_instance(
            image=image,
            owner=kwargs['owner'],
            context=kwargs.get('context')
        )

        return image_instance
