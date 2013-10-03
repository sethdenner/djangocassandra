import copy

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


from knotis.views import (
    ContextView
)

from knotis.contrib.layout.views import GridSmallView

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)

from knotis.contrib.offer.models import Offer
from knotis.contrib.offer.views import OfferTile


class MyEstablishmentsView(ContextView):
    template_name = 'knotis/merchant/my_establishments_view.html'

    def process_context(self):
        return self.context


class MyOffersGrid(GridSmallView):
    view_name = 'my_offers_grid'

    def process_context(self):
        request = self.context.get('request')
        current_identity_id = request.session.get('current_identity_id')
        current_identity = get_object_or_404(Identity, pk=current_identity_id)

        try:
            managed_identities = Identity.objects.get_managed(current_identity)

        except Exception:
            logger.exception('could not get managed identities')
            return self.context

        offers_by_business = {}

        offer_filter = self.context.get('offer_filter')
        offer_filter_dict = {}
        if 'active' == offer_filter:
            offer_filter_dict['active'] = True
            offer_filter_dict['published'] = True

        elif 'pending':
            offer_filter_dict['active'] = True
            offer_filter_dict['published'] = False

        elif 'completed':
            offer_filter_dict['completed'] = True

        for i in managed_identities:
            if i.identity_type != IdentityTypes.BUSINESS:
                continue

            offer_filter_dict['owner'] = i

            try:
                offers_by_business[i.name] = Offer.objects.filter(
                    **offer_filter_dict
                )

            except Exception:
                logger.exception(''.join([
                    'failed to get offers for business ',
                    i.name,
                    '.'
                ]))
                continue

        tiles = []
        for key, value in offers_by_business.iteritems():
            for offer in value:
                tile = OfferTile()
                tiles.append(tile.render_template_fragment({
                    'offer': offer
                }))

        local_context = copy.copy(self.context)
        local_context['tiles'] = tiles

        return local_context


class MyOffersView(ContextView):
    template_name = 'knotis/merchant/my_offers_view.html'

    @login_required
    def disptach(
        self,
        *args,
        **kwargs
    ):
        return super(MyOffersView, self).dispatch(
            *args,
            **kwargs
        )

    def process_context(self):
        styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
        ]

        pre_scripts = []

        post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'knotis/layout/js/create.js',
            'navigation/js/navigation.js',
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
        })
        return local_context


class OfferRedemptionView(ContextView):
    template_name = 'knotis/merchant/offer_redemption_view.html'

    def process_context(self):
        return self.context


class MyFollowersView(ContextView):
    template_name = 'knotis/merchant/my_followers_view.html'

    def process_context(self):
        return self.context


class MyAnalyticsView(ContextView):
    template_name = 'knotis/merchant/my_analytics_view.html'

    def process_context(self):
        return self.context
