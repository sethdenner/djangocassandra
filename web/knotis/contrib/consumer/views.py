import copy

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.template import (
    RequestContext
)

from knotis.views import (
    ContextView
)

from knotis.contrib.layout.views import GridSmallView


from knotis.contrib.identity.models import Identity
from knotis.contrib.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.contrib.identity.views import (
    TransactionTileView
)


class MyPurchasesGrid(GridSmallView):
    view_name = 'my_purchases_grid'

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

        purchase_filter = self.context.get(
            'purchase_filter',
            'unused'
        )
        if None is purchase_filter:
            purchase_filter = 'unused'

        purchase_filter = purchase_filter.lower()
        unused = purchase_filter == 'unused'

        purchases = Transaction.objects.filter(
            owner=current_identity,
            transaction_type=TransactionTypes.PURCHASE
        )

        for purchase in purchases:
            if purchase.reverted:
                continue

            if unused != purchase.has_redemptions():
                merchant = purchase.offer.owner

                redemption_tile = TransactionTileView()
                tile_context = RequestContext(
                    request, {
                        'redeem': False,
                        'show_offer_info': True,
                        'transaction': purchase,
                        'identity': merchant,
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


class MyPurchasesView(ContextView):
    template_name = 'knotis/consumer/my_purchases_view.html'

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
            'knotis/merchant/js/redemptions.js'
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'top_menu_name': 'my_purchases',
            'fixed_side_nav': True
        })

        return local_context


class MyRelationsView(ContextView):
    template_name = 'knotis/consumer/my_relations_view.html'

    def process_context(self):
        return self.context
