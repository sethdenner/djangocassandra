import copy

from weasyprint import HTML

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.shortcuts import get_object_or_404

from django.core.exceptions import PermissionDenied

from django.template import (
    RequestContext
)

from django.http import (
    HttpResponse,
    HttpResponseServerError
)

from django.views.generic import View

from knotis.views import (
    FragmentView,
    ContextView,
    EmbeddedView,
    PaginationMixin,
)

from knotis.contrib.layout.views import (
    GridSmallView,
    DefaultBaseView
)

from knotis.contrib.identity.models import (
    IdentityTypes
)
from knotis.contrib.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.contrib.identity.views import (
    get_current_identity,
    get_identity_profile_banner,
    get_identity_profile_badge,
    TransactionTileView
)
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin


class MyPurchasesGrid(GridSmallView, PaginationMixin, GetCurrentIdentityMixin):
    view_name = 'my_purchases_grid'

    def get_queryset(self):
        current_identity = self.get_current_identity(self.request)

        return Transaction.objects.filter(
            owner=current_identity,
            transaction_type=TransactionTypes.PURCHASE
        )

    def process_context(self):

        request = self.request
        current_identity = self.get_current_identity(request)

        if not current_identity:
            return self.context

        purchases = self.get_page(self.context)

        purchase_filter = self.context.get(
            'purchase_filter',
        )
        if None is purchase_filter:
            purchase_filter = 'unused'

        purchase_filter = purchase_filter.lower()
        unused = purchase_filter == 'unused'

        tiles = []

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
                        'IdentityTypes': IdentityTypes,
                        'offer': purchase.offer,
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


class MyPurchasesView(EmbeddedView):
    template_name = 'knotis/consumer/my_purchases_view.html'
    url_patterns = [
        '^purchases(/(?P<purchase_filter>\w*))?/$',
    ]
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'knotis/layout/js/pagination.js',
        'knotis/consumer/js/purchases.js',
    ]

    def process_context(self):

        local_context = copy.copy(self.context)
        local_context.update({
            'top_menu_name': 'my_purchases',
            'fixed_side_nav': True
        })

        return local_context


class MyRelationsView(ContextView):
    template_name = 'knotis/consumer/my_relations_view.html'

    def process_context(self):
        return self.context


class PrintedVoucher(FragmentView):
    template_name = 'knotis/consumer/printable_voucher.html'
    view_name = 'printed_voucher'

    def process_context(self):
        request = self.context.get('request')
        current_identity = get_current_identity(request)

        transaction_id = self.context.get('transaction_id')
        transaction = get_object_or_404(
            Transaction,
            pk=transaction_id,
            transaction_type=TransactionTypes.PURCHASE
        )

        if transaction.owner != current_identity:
            message = 'This transaction does not belong to this user.'
            logger.error(message)
            raise PermissionDenied(message)

        static_files = self.context.get('static_files')
        if not static_files:
            static_files = settings.STATIC_URL_ABSOLUTE

        business_cover = get_identity_profile_banner(transaction.offer.owner)
        business_logo = get_identity_profile_badge(transaction.offer.owner)

        self.context.update({
            'transaction': transaction,
            'business_cover': business_cover,
            'business_logo': business_logo,
            'static_files': static_files,
            'BASE_URL': settings.BASE_URL
        })

        return self.context


class DownloadPrintedVoucher(View):
    VOUCHER_SAVE_LOCATION = ''

    def get(
        self,
        request,
        transaction_id=None,
        *args,
        **kwargs
    ):
        voucher_view = PrintedVoucher()
        voucher_html = voucher_view.render_template_fragment(RequestContext(
            request, {
                'transaction_id': transaction_id,
                'static_files': ''.join([
                    'file://',
                    settings.STATIC_ROOT
                ])
            }
        ))

        filename = 'redemption_code.pdf'

        html = HTML(
            media_type='screen',
            string=voucher_html
        )

        try:
            html.write_pdf(filename)

        except Exception:
            logger.exception('Failed to write pdf file.')
            return HttpResponseServerError(
                'Failed to generate voucher pdf.'
            )

        fp = open(filename, 'rb')
        response = HttpResponse(
            fp.read(),
            content_type='application/pdf'
        )
        fp.close()

        response['Content-Disposition'] = ''.join([
            'attachment; filename="',
            filename,
            '"'
        ])

        return response
