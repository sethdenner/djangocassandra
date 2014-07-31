import copy
import random
import string

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template import (
    Context,
    RequestContext
)
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.utils.regex import REGEX_UUID

from knotis.contrib.offer.models import (
    Offer,
    OfferItem,
)
from knotis.contrib.product.models import (
    Product,
    CurrencyCodes
)
from knotis.contrib.inventory.models import (
    Inventory
)
from knotis.contrib.media.models import ImageInstance
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)
from knotis.contrib.identity.views import get_identity_profile_badge

from knotis.contrib.paypal.views import IPNCallbackView

from knotis.contrib.transaction.api import TransactionApi

from knotis.contrib.stripe.views import (
    StripeButton
)

from knotis.views import (
    ContextView,
    EmbeddedView,
    ModalView,
    AJAXFragmentView,
    FragmentView,
    EmailView
)

from knotis.contrib.layout.views import (
    ActionButton,
    DefaultBaseView,
    GridSmallView
)


class OfferPurchaseButton(AJAXFragmentView):
    template_name = 'knotis/offer/offer_purchase_button.html'
    view_name = 'purchse_button'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_object_or_404(
            Identity,
            pk=request.session['current_identity']
        )
        offer_id = request.POST['offerId']
        quantity = request.POST['quantity']

        try:
            offer = Offer.objects.get(pk=offer_id)

        except:
            offer = None

        if not offer:
            return self.generate_ajax_response({
                'errors': {'no-field': 'Could not find offer'},
                'status': 'ERROR'
            })

        if not offer.available():
            return self.generate_ajax_response({
                'errors': {
                    'no-field': 'This offer is no longer available'
                },
                'status': 'ERROR'
            })

        try:
            mode = 'none'
            for i in range(int(quantity)):
                redemption_code = ''.join(
                    random.choice(
                        string.ascii_uppercase + string.digits
                    ) for _ in range(10)
                )

                transaction_context = '|'.join([
                    current_identity.pk,
                    IPNCallbackView.generate_ipn_hash(current_identity.pk),
                    redemption_code,
                    mode
                ])

                usd = Product.currency.get(CurrencyCodes.USD)
                buyer_usd = Inventory.objects.get_stack(
                    current_identity,
                    usd,
                    create_empty=True
                )

                TransactionApi.create_purchase(
                    request=request,
                    offer=offer,
                    buyer=current_identity,
                    currency=buyer_usd,
                    transaction_context=transaction_context
                )

        except Exception, e:
            logger.exception(e.message)
            return self.generate_ajax_response({
                'status': 'ERROR',
                'errors': {'no-field': e.message}
            })

        return self.generate_ajax_response({
            'status': 'OK'
        })


class OffersGridView(GridSmallView):
    view_name = 'offers_grid'

    def process_context(self):
        request = self.request
        current_identity = None
        if request.user.is_authenticated():
            current_identity_id = request.session['current_identity']
            try:
                current_identity = Identity.objects.get(pk=current_identity_id)

            except:
                pass

        if (
            current_identity and
            current_identity.identity_type == IdentityTypes.INDIVIDUAL
        ):
            offer_action = 'buy'

        else:
            offer_action = None

        offer_filter_dict = {
            'published': True,
            'active': True,
            'completed': False
        }

        try:
            offers = Offer.objects.filter(
                **offer_filter_dict
            )

        except Exception:
            logger.exception(''.join([
                'failed to get offers.'
            ]))

        tiles = []
        for offer in offers:
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


class OffersView(EmbeddedView):
    url_patterns = [
        r''.join([
            '^s/(?P<offer_id>',
            REGEX_UUID,
            '/)?$'
        ])
    ]

    default_parent_view_class = DefaultBaseView
    template_name = 'knotis/offer/offers_view.html'

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
            'knotis/offer/js/offers.js',
            'knotis/strips/js/stripe_form.js'
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
        })
        return local_context


class OfferPurchaseSuccessView(ModalView):
    view_name = 'offer_purchase_success'
    template_name = 'knotis/offer/offer_purchase_success.html'
    url_patterns = [
        r''.join([
            '/(?P<offer_id>',
            REGEX_UUID,
            ')/buy/success/$'
        ])
    ]


class OfferPurchaseView(EmbeddedView):
    template_name = 'knotis/offer/offer_purchase_view.html'
    url_patterns = [
        r''.join([
            '/(?P<offer_id>',
            REGEX_UUID,
            ')/buy/$'
        ])
    ]
    default_parent_view_class = DefaultBaseView

    def process_context(self):
        request = self.context.get('request')

        styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'knotis/offer/css/offer_purchase.css'
        ]
        self.context['styles'] = styles

        post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'navigation/js/navigation.js',
            'knotis/offer/js/offer_purchase.js',
            'knotis/offer/js/offer_purchase_button.js',
            'knotis/stripe/js/stripe_form.js'
        ]
        self.context['post_scripts'] = post_scripts

        offer_id = self.context.get('offer_id')
        offer = get_object_or_404(Offer, pk=offer_id)
        self.context['offer'] = offer
        self.context['settings'] = settings

        try:
            business_badge = ImageInstance.objects.get(
                related_object_id=offer.owner.pk,
                context='profile_badge',
                primary=True
            )

        except:
            business_badge = None

        if offer.price_discount() > 0.:
            stripe_button = StripeButton()
            stripe_button_context = RequestContext(
                request, {
                    'STRIPE_API_KEY': settings.STRIPE_API_KEY,
                    'STATIC_URL': settings.STATIC_URL,
                    'BASE_URL': settings.BASE_URL,
                    'business_name': offer.owner.name,
                    'offer_title': offer.title,
                    'offer_price': offer.price_discount(),
                    'business_badge': business_badge,
                    'offer_id': offer.pk
                }
            )
            self.context['purchase_button'] = (
                stripe_button.render_template_fragment(
                    stripe_button_context
                )
            )

        else:
            free_button = OfferPurchaseButton()
            free_button_context = RequestContext(
                request, {
                    'offer_id': offer.pk,
                    'amount': offer.price_discount()
                }
            )
            self.context['purchase_button'] = (
                free_button.render_template_fragment(
                    free_button_context
                )
            )

        return self.context


class OfferActionButton(ActionButton):
    view_name = 'offer_action_button'


class OfferTile(FragmentView):
    template_name = 'knotis/offer/tile.html'
    view_name = 'offer_tile'
    offer_stats = 'osdfisdjf'

    def process_context(self):
        offer = self.context.get('offer', None)

        if not offer:
            return self.context

        try:
            offer_banner_image = ImageInstance.objects.get(
                related_object_id=offer.id,
                context='offer_banner',
                primary=True
            )

        except:
            logger.exception('failed to get offer banner image')
            offer_banner_image = None

        try:
            business_badge_image = get_identity_profile_badge(offer.owner)

        except:
            logger.exception('failed to get business badge image')
            business_badge_image = None

        # TODO: CALCULATE STATS.
        self.context.update({
            'offer_banner_image': offer_banner_image,
            'business_badge_image': business_badge_image,
        })
        return self.context


class OfferDetailView(ModalView):
    template_name = 'knotis/offer/detail.html'
    view_name = 'offer_detail'
    url_patterns = [
        r''.join([
            'detail/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ]),
    ]
    default_parent_view_class = DefaultBaseView

    def process_context(self):
        offer_id = self.context.get('offer_id')
        offer = get_object_or_404(Offer, pk=offer_id)

        offer_items = self.context.get('offer_items')
        if not offer_items:
            try:
                offer_items = OfferItem.objects.filter(offer=offer)

            except Exception:
                logger.exception('failed to get offer items')
                offer_items = None

        try:
            business_badge_image = ImageInstance.objects.get(
                related_object_id=offer.owner_id,
                context='profile_badge',
                primary=True
            )

        except:
            logger.exception('failed to get business badge image')
            business_badge_image = None

        request = self.request
        current_identity_id = request.session.get('current_identity')
        try:
            current_identity = Identity.objects.get(pk=current_identity_id)

        except:
            current_identity = None

        local_context = copy.copy(self.context)
        local_context.update({
            'current_identity': current_identity,
            'IdentityTypes': IdentityTypes,
            'offer': offer,
            'offer_items': offer_items,
            'business_badge_image': business_badge_image
        })

        return local_context


class NewOfferEmailBody(EmailView):
    template_name = 'knotis/offer/email_new_offer.html'
    text_template_name = 'knotis/offer/email_new_offer.txt'

    def process_context(self):
        local_context = copy.copy(self.context)

        browser_link = 'example.com'
        product_title = 'Grilled Cheese Sandwich'
        product_img_url = '/media/cache/ef/25/ef2517885c028d7545f13f79e5b7993a.jpg'
        business_logo_url = '/media/cache/87/08/87087ae77f4a298e550fc9d255513ad4.jpg'
        purchase_link = 'example.com'
        price = "$20.00"

        local_context.update({
            'browser_link': browser_link,
            'product_title': product_title,
            'product_img_url': product_img_url,
            'business_logo_url': business_logo_url,
            'purchase_link': purchase_link,
            'price': price
        })

        return local_context
