import copy

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template import (
    Context,
    RequestContext
)

from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.layout.views import (
    GridSmallView,
    DefaultBaseView,
)

from knotis.views import (
    EmbeddedView,
)

from knotis.contrib.offer.models import (
    Offer,
    OfferItem,
    OfferTypes,
    OfferCollection,
    OfferCollectionItem,
)

from knotis.contrib.offer.views import (
    CollectionTile,
    OfferTile,
)


class PassportView(EmbeddedView):
    url_patterns = [
        r'^passport/$'
    ]
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'knotis/offer/js/offers.js',
    ]
    template_name = 'knotis/passport/passport_view.html'
    
    
class PassportGridView(GridSmallView):
    view_name = 'passport_grid'

    def process_context(self):
        request = self.request
        current_identity = None
        if request.user.is_authenticated():
            current_identity_id = request.session['current_identity']
            try:
                current_identity = Identity.objects.get(pk=current_identity_id)

            except:
                pass

        page = int(self.context.get('page', '0'))
        count = int(self.context.get('count', '20'))
        start_range = page * count
        end_range = start_range + count

        offer_filter_dict = {
            'published': True,
            'active': True,
            'completed': False,
            'offer_type': OfferTypes.DIGITAL_OFFER_COLLECTION,
        }

        try:
            collections = Offer.objects.filter(
                **offer_filter_dict
            )[start_range:end_range]

        except Exception:
            logger.exception(''.join([
                'failed to get list of passports.'
            ]))
            collections = []

        tiles = []
        for collection in collections:
            if collection.offer_type == OfferTypes.DIGITAL_OFFER_COLLECTION:
                tile = CollectionTile()
                tiles.append(tile.render_template_fragment(Context({
                    'offer': collection,
                    'current_identity': current_identity,
                })))

            else:
                # I shouldn't be hit because of how query is ran.
                # Left here just in case I don't understand digital collections.
                tile = OfferTile()
                tiles.append(tile.render_template_fragment(Context({
                    'offer': collection,
                    'current_identity': current_identity,
                })))

        local_context = copy.copy(self.context)
        local_context.update({
            'tiles': tiles
        })
        return local_context
