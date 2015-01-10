import datetime
from knotis.contrib.identity.tests.utils import IdentityModelTestUtils
from knotis.contrib.media.tests.utils import MediaTestUtils
from knotis.contrib.offer.api import (
    OfferApi,
    OfferTypes
)


class OfferTestUtils(object):
    @staticmethod
    def create_test_offer(
        **kwargs
    ):
        if not kwargs.get('owner'):
            kwargs[
                'owner'
            ] = IdentityModelTestUtils.create_test_establishment()

        if not kwargs.get('offer_type'):
            kwargs['offer_type'] = OfferTypes.NORMAL

        if not kwargs.get('title'):
            kwargs['title'] = 'Test offer title'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test offer description'

        if not kwargs.get('default_image'):
            kwargs['default_image'] = MediaTestUtils.create_test_image(
                owner=kwargs['owner']
            )

        if not kwargs.get('published'):
            kwargs['published'] = True

        if not kwargs.get('active'):
            kwargs['active'] = True

        if not kwargs.get('completed'):
            kwargs['completed'] = False

        if not kwargs.get('restrictions'):
            kwargs['restrictions'] = 'Test offer restrictions'

        if not kwargs.get('stock'):
            kwargs['stock'] = 10

        if not kwargs.get('start_date'):
            kwargs['start_date'] = datetime.datetime.utcnow()

        if not kwargs.get('end_date'):
            kwargs['end_date'] = kwargs['start_date'] + datetime.timedelta(
                days=7
            )

        offer = OfferApi.create_offer(**kwargs)

        #offer.default_image.related_object_id = offer.id
        #offer.default_image.save()

        return offer
