import copy
from itertools import chain

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.template import (
    Context,
    RequestContext
)

from knotis.contrib.layout.views import GridSmallView

from knotis.views import (
    ContextView,
    FragmentView
)

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)

from knotis.contrib.offer.models import Offer
from knotis.contrib.offer.views import (
    OfferTile,
    OfferCreateTile
)

from knotis.contrib.identity.views import (
    IdentityTile
)

from knotis.contrib.identity.models import (
    IdentityIndividual,
    IdentityEstablishment
)

from knotis.contrib.transaction.models import (
    Transaction,
    TransactionItem,
    TransactionTypes
)
from knotis.contrib.transaction.views import (
    TransactionTileView
)


class RedemptionsGrid(GridSmallView):
    view_name = 'redemptions_grid'

    def process_context(self):
        tiles = []

        request = self.request
        session = request.session

        current_identity_id = session['current_identity_id']

        try:
            current_identity = Identity.objects.get(pk=current_identity_id)

        except:
            logger.exception('Failed to get current identity')
            raise

        purchases = Transaction.objects.filter(
            owner=current_identity,
            transaction_type=TransactionTypes.PURCHASE
        )

        for purchase in purchases:
            if purchase.reverted:
                continue

            if not purchase.redemptions():
                transaction_items = TransactionItem.objects.filter(
                    transaction=purchase
                )

                consumer = None

                for i in transaction_items:
                    recipient = i.inventory.recipient
                    if recipient.pk == current_identity.pk:
                        continue

                    consumer = recipient
                    break

                redemption_tile = TransactionTileView()
                tile_context = RequestContext(
                    request, {
                        'redeem': True,
                        'transaction': purchase,
                        'identity': consumer,
                        'TransactionTypes': TransactionTypes
                    }
                )
                tiles.append(
                    redemption_tile.render_template_fragment(
                        tile_context
                    )
                )

        self.context.update({
            'tiles': tiles
        })

        return self.context


class MyRedemptionsView(ContextView):
    template_name = 'knotis/merchant/my_redemptions_view.html'

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
            'navigation/js/navigation.js',
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'fixed_side_nav': True
        })

        return local_context


class MyCustomersGrid(GridSmallView):
    view_name = 'my_customers_grid'

    def process_context(self):
        tiles = []

        request = self.request
        session = request.session

        current_identity_id = session['current_identity_id']

        try:
            current_identity = Identity.objects.get(pk=current_identity_id)

        except:
            logger.exception('Failed to get current identity')
            raise

        purchases = Transaction.objects.filter(
            owner=current_identity,
            transaction_type=TransactionTypes.PURCHASE
        )

        tile_contexts = []

        def add_context(
            identity,
            transaction,
            contexts
        ):
            for c in contexts:
                if c['identity'].pk == identity.pk:
                    if c['transaction'].pub_date < transaction.pub_date:
                        c['transaction'] = transaction
                        break

            contexts.append({
                'identity': identity,
                'transaction': transaction
            })

        for p in purchases:
            if p.reverted:
                continue

            transaction_items = TransactionItem.objects.filter(
                transaction=p
            )

            for i in transaction_items:
                recipient = i.inventory.recipient
                if recipient.pk == current_identity.pk:
                    continue

                add_context(
                    recipient,
                    p,
                    tile_contexts
                )

        for c in tile_contexts:
            customer_tile = TransactionTileView()
            customer_tile_context = RequestContext(
                request,
                c
            )
            tiles.append(
                customer_tile.render_template_fragment(
                    customer_tile_context
                )
            )

        self.context['tiles'] = tiles
        return self.context


class MyCustomersView(ContextView):
    template_name = 'knotis/merchant/my_customers.html'

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
            'navigation/js/navigation.js',
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'fixed_side_nav': True
        })

        return local_context


class MyEstablishmentsView(ContextView):
    template_name = 'knotis/merchant/my_establishments_view.html'

    def process_context(self):

        styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'styles/default/fileuploader.css'
        ]

        pre_scripts = []

        post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/create.js',
            'navigation/js/navigation.js',
            'jcrop/js/jquery.Jcrop.js',
            'scripts/fileuploader.js',
            'scripts/jquery.colorbox.js',
            'scripts/jquery.sickle.js',
            'knotis/identity/js/profile.js',
            'knotis/api/js/api.js',
            'knotis/identity/js/business-tile.js'
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'fixed_side_nav': True
        })

        return local_context


class MyEstablishmentsGrid(GridSmallView):
    view_name = 'my_establishments_grid'

    def process_context(self):
        tiles = []

        request = self.request
        if request.user.is_authenticated():
            user_identity = IdentityIndividual.objects.get_individual(
                request.user
            )
            establishments = IdentityEstablishment.objects.get_establishments(
                user_identity
            )
            if establishments:
                for establishment in establishments:
                    establishment_tile = IdentityTile()
                    establishment_context = Context({
                        'identity': establishment,
                        'request': request
                    })
                    tiles.append(
                        establishment_tile.render_template_fragment(
                            establishment_context
                        )
                    )

        local_context = copy.copy(self.context)
        local_context.update({
            'tiles': tiles,
            'tile_link_template': '/id/',
            'request': request
        })

        return local_context


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
        if 'pending' == offer_filter:
            offer_filter_dict['published'] = False
            offer_action = 'edit'

        elif 'completed' == offer_filter:
            offer_filter_dict['completed'] = True
            offer_action = None

        elif 'active' == offer_filter or not offer_filter:
            offer_filter_dict['published'] = True
            offer_action = 'pause'

        elif 'redeem' == offer_filter:
            offer_filter_dict['active'] = True
            offer_action = 'redeem'

        else:
            raise Http404()

        identities = [current_identity]
        identities = list(chain(identities, managed_identities))

        for i in identities:
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

        offer_create_tile = OfferCreateTile()
        tiles.append(
            offer_create_tile.render_template_fragment(Context({
                'create_type': 'Promotion',
                'create_action': '/offer/create/',
                'action_type': 'modal'
            }))
        )

        for key, value in offers_by_business.iteritems():
            for offer in value:
                tile = OfferTile()
                tiles.append(tile.render_template_fragment(Context({
                    'offer': offer,
                    'offer_action': offer_action
                })))

        local_context = copy.copy(self.context)
        local_context.update({
            'tiles': tiles
        })
        return local_context


class MyOffersView(ContextView):
    template_name = 'knotis/merchant/my_offers_view.html'

    def process_context(self):
        styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'styles/default/fileuploader.css'
            'knotis/merchant/css/my_offers.css'
        ]

        pre_scripts = []

        post_scripts = [
            'jcrop/js/jquery.Jcrop.js',
            'scripts/fileuploader.js',
            'scripts/jquery.colorbox.js',
            'scripts/jquery.sickle.js',
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'knotis/layout/js/create.js',
            'navigation/js/navigation.js',
            'knotis/merchant/js/my_offers.js'
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'top_menu_name': 'my_offers',
            'fixed_top_nav': True,
            'fixed_side_nav': True
        })
        return local_context


class OfferRedemptionView(FragmentView):
    template_name = 'knotis/merchant/redemption_view.html'
    view_name = 'offer_redemption'

    def process_context(self):
        self.context = copy.copy(self.context)

        request = self.context.get('request')

        offer_id = self.context.get('offer_id')
        offer = Offer.objects.get(pk=offer_id)

        current_identity_id = request.session.get('current_identity_id')
        current_identity = Identity.objects.get(pk=current_identity_id)

        purchases = Transaction.objects.filter(
            offer=offer,
            transaction_type=TransactionTypes.PURCHASE
        )

        consumer_purchases = []
        for purchase in purchases:
            if purchase.owner != current_identity:
                if not purchase.redemptions():
                    consumer_purchases.append(purchase)

        offer_tile = OfferTile()
        offer_tile_markup = offer_tile.render_template_fragment(Context({
            'offer': offer
        }))

        self.context.update({
            'offer': offer,
            'purchases': consumer_purchases,
            'offer_tile_markup': offer_tile_markup
        })

        return self.context


class MyFollowersView(ContextView):
    template_name = 'knotis/merchant/my_followers_view.html'

    def process_context(self):
        return self.context


class MyAnalyticsView(ContextView):
    template_name = 'knotis/merchant/my_analytics_view.html'

    def process_context(self):
        return self.context
