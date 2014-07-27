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

from knotis.contrib.layout.views import (
    GridSmallView,
    DefaultBaseView,
)

from knotis.views import (
    ContextView,
    FragmentView,
    EmbeddedView,
    GenerateAjaxResponseMixin
)

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes,
    IdentityIndividual,
    IdentityEstablishment
)

from knotis.contrib.offer.models import Offer, OfferTypes
from knotis.contrib.offer.views import (
    OfferTile,
    OfferCreateTile
)

from knotis.contrib.identity.views import (
    IdentityTile,
    TransactionTileView
)
from knotis.contrib.transaction.models import (
    Transaction,
    TransactionItem,
    TransactionTypes
)
from knotis.contrib.transaction.api import TransactionApi


class RedemptionsGrid(GridSmallView):
    view_name = 'redemptions_grid'

    def process_context(self):
        tiles = []

        request = self.request
        session = request.session

        current_identity_id = session['current_identity']

        try:
            current_identity = Identity.objects.get(pk=current_identity_id)

        except:
            logger.exception('Failed to get current identity')
            raise

        redemption_filter = self.context.get(
            'redemption_filter',
            'unredeemed'
        )
        if None is redemption_filter:
            redemption_filter = 'unredeemed'

        redemption_filter = redemption_filter.lower()
        redeemed = redemption_filter == 'redeemed'

        purchases = Transaction.objects.filter(
            owner=current_identity,
            transaction_type=TransactionTypes.PURCHASE
        )

        for purchase in purchases:
            if purchase.reverted:
                continue

            if redeemed == purchase.has_redemptions():
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
                        'redeem': not redeemed,
                        'transaction': purchase,
                        'identity': consumer,
                        'TransactionTypes': TransactionTypes
                    }
                )

                try:
                    tiles.append(
                        redemption_tile.render_template_fragment(
                            tile_context
                        )
                    )
                except:
                    logger.exception('Failed to render transaction view for %s' % purchase)
                    continue

        self.context.update({
            'tiles': tiles
        })

        return self.context


class MyRedemptionsView(EmbeddedView, GenerateAjaxResponseMixin):
    url_patterns = [
        r'^redemptions(/(?P<redemption_filter>\w*))?/$',
    ]

    default_parent_view_class = DefaultBaseView
    template_name = 'knotis/merchant/my_redemptions_view.html'

    def process_context(self):
        styles = [
        ]

        pre_scripts = []

        post_scripts = [
            'knotis/merchant/js/redemptions.js'
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'top_menu_name': 'my_redemptions'
        })

        return local_context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity_id = request.session.get('current_identity')

        try:
            current_identity = Identity.objects.get(pk=current_identity_id)

        except Exception, e:
            return self.generate_ajax_response({
                'errors': {
                    'no-field': e.message
                },
                'status': 'ERROR'
            })

        data = request.POST

        transaction_id = data.get('transactionid')
        transaction = get_object_or_404(
            Transaction,
            pk=transaction_id
        )

        if current_identity.pk != transaction.owner.pk:
            return self.generate_ajax_response({
                'errors': {
                    'no-field': 'This transaction does not belong to you'
                },
                'status': 'ERROR'
            })

        try:

            redemptions = TransactionApi.create_redemption(
                request,
                transaction,
                current_identity
            )

        except Exception, e:
            return self.generate_ajax_response({
                'errors': {
                    'no-field': e.message
                },
                'status': 'ERROR'
            })

        if redemptions[0].owner.pk == current_identity.pk:
            my_redemption = redemptions[0]

        else:
            my_redemption = redemptions[1]

        return self.generate_ajax_response({
            'status': 'OK',
            'redemptionid': my_redemption.pk
        })


class MyCustomersGrid(GridSmallView):
    view_name = 'my_customers_grid'

    def process_context(self):
        tiles = []

        request = self.request
        session = request.session

        current_identity_id = session.get('current_identity')

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


class MyCustomersView(EmbeddedView):
    url_patterns = [
        r'^customers/$',
    ]

    default_parent_view_class = DefaultBaseView
    template_name = 'knotis/merchant/my_customers.html'

    def process_context(self):
        styles = [
        ]

        pre_scripts = []

        post_scripts = [
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
        current_identity_id = request.session.get('current_identity')
        current_identity = get_object_or_404(Identity, pk=current_identity_id)

        try:
            managed_identities = Identity.objects.get_managed(current_identity)

        except Exception:
            logger.exception('could not get managed identities')
            return self.context

        offers_by_establishment = {}

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
            offer_filter_dict['completed'] = False
            offer_action = 'pause'

        elif 'redeem' == offer_filter:
            offer_filter_dict['active'] = True
            offer_action = 'redeem'

        else:
            raise Http404()

        identities = [current_identity]
        identities = list(chain(identities, managed_identities))

        for i in identities:
            if i.identity_type != IdentityTypes.ESTABLISHMENT:
                continue

            offer_filter_dict['owner'] = i

            try:
                offers_by_establishment[i.name] = filter(
                    lambda x: x.offer_type != OfferTypes.DARK,
                    Offer.objects.filter(
                        **offer_filter_dict
                    )
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

        for key, value in offers_by_establishment.iteritems():
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


class MyOffersView(EmbeddedView):
    view_name = 'my_offers'
    template_name = 'knotis/merchant/my_offers_view.html'
    url_patterns = [
        r'^offers(/(?P<offer_filter>\w*))?/$',
    ]
    default_parent_view_class = DefaultBaseView
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


class OfferRedemptionView(FragmentView):
    template_name = 'knotis/merchant/redemption_view.html'
    view_name = 'offer_redemption'

    def process_context(self):
        self.context = copy.copy(self.context)

        request = self.context.get('request')

        offer_id = self.context.get('offer_id')
        offer = Offer.objects.get(pk=offer_id)

        current_identity_id = request.session.get('current_identity')
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


class MyAnalyticsView(ContextView):
    template_name = 'knotis/merchant/my_analytics_view.html'

    def process_context(self):
        return self.context
