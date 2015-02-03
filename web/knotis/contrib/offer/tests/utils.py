import datetime
from knotis.contrib.identity.tests.utils import IdentityModelTestUtils
from knotis.contrib.media.tests.utils import MediaTestUtils
from knotis.contrib.offer.models import (
    OfferCollection,
    OfferCollectionItem
)
from knotis.contrib.offer.api import (
    OfferApi,
    OfferTypes
)
import random


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

        offer.default_image = MediaTestUtils.create_test_image(
            owner=kwargs['owner'],
            context='offer_banner'
        )

        offer.default_image.related_object_id = offer.id
        offer.default_image.save()
        offer.save()

        return offer

    @staticmethod
    def create_test_offer_collection(
        **kwargs
    ):
        unique = str(random.randint(0, 100000))
        if not kwargs.get('neighborhood'):
            kwargs['neighborhood'] = 'Seattle neighborhood' + unique

        if not kwargs.get('owner'):
            kwargs[
                'owner'
            ] = IdentityModelTestUtils.create_test_establishment(
                name='Knotis INC'
            )

        if not kwargs.get('value'):
            kwargs['value'] = float(random.randint(400, 700))

        if not kwargs.get('price'):
            kwargs['price'] = float(random.randint(10, 30))

        offer_collection = OfferCollection.objects.create(
            neighborhood=kwargs['neighborhood']
        )

        numb_offers = kwargs.get('numb_offers', random.randint(10, 20))

        for page_num in xrange(numb_offers):
            value = random.randint(20, 100)
            minimum = random.randint(5, 20)
            title = '$%s credit toward any purchase' % value
            restrictions = '$%s Minimum' % minimum
            owner = IdentityModelTestUtils.create_test_establishment()

            new_offer = OfferTestUtils.create_test_offer(
                restrictions=restrictions,
                owner=owner,
                title=title,
                is_physical=False,
                offer_type=OfferTypes.DARK
            )
            OfferCollectionItem.objects.create(
                offer=new_offer,
                page=page_num,
                offer_collection=offer_collection,
            )

        kwargs.update({
            'description': offer_collection.pk,
            'is_physical': False,
            'offer_type': OfferTypes.DIGITAL_OFFER_COLLECTION,
            'title': kwargs['neighborhood'],
        })

        offer_collection_offer = OfferTestUtils.create_test_offer(
            **kwargs
        )
        offer_collection_offer.active = True
        offer_collection_offer.published = True
        offer_collection_offer.save()

        return offer_collection
