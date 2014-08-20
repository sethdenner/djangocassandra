import json
import copy
from itertools import chain

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.shortcuts import get_object_or_404

from django.http import (
    Http404,
    HttpResponseServerError
)
from django.template import (
    Context,
    RequestContext
)

from django.core.exceptions import PermissionDenied

from knotis.utils.view import format_currency
from knotis.utils.regex import REGEX_UUID

from knotis.contrib.layout.views import (
    GridSmallView,
    DefaultBaseView,
)

from knotis.views import (
    ContextView,
    FragmentView,
    EmbeddedView,
    ModalView,
    AJAXFragmentView,
    GenerateAjaxResponseMixin
)

from knotis.contrib.auth.models import UserInformation
from knotis.contrib.media.models import ImageInstance
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes,
    EndpointTypeNames,
    EndpointEmail,
    EndpointYelp,
    EndpointFacebook,
    EndpointTwitter,
    EndpointPhone,
    EndpointWebsite,
)

from knotis.contrib.offer.models import (
    Offer,
    OfferItem,
    OfferAvailability,
    OfferTypes,
    OfferPublish
)

from knotis.contrib.offer.views import (
    OfferTile,
    DummyOfferTile,
)

from knotis.contrib.wizard.views import (
    WizardView,
    WizardStepView
)

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes,
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment
)
from knotis.contrib.identity.views import (
    IdentityTile,
    IdentityActionButton,
    TransactionTileView,
    get_identity_profile_badge,
    get_identity_profile_banner,
    get_identity_default_profile_banner_color
)
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.identity.api import IdentityApi


from knotis.contrib.product.models import (
    Product,
    ProductTypes
)
from knotis.contrib.inventory.models import Inventory

from knotis.contrib.transaction.models import (
    Transaction,
    TransactionItem,
    TransactionTypes
)
from knotis.contrib.transaction.api import TransactionApi
from knotis.contrib.location.models import (
    Location,
    LocationItem
)

from knotis.contrib.twitter.views import get_twitter_feed_json
from knotis.contrib.yelp.views import get_reviews_by_yelp_id


from .forms import (
    OfferProductPriceForm,
    OfferDetailsForm,
    OfferPhotoLocationForm,
    OfferPublicationForm,
    OfferFinishForm
)


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
                    logger.exception(
                        'Failed to render transaction view for %s' % purchase
                    )
                    continue

        self.context.update({
            'tiles': tiles
        })

        return self.context


class MyRedemptionsView(EmbeddedView, GenerateAjaxResponseMixin):
    url_patterns = [
        r'^my/redemptions(/(?P<redemption_filter>\w*))?/$',
    ]

    default_parent_view_class = DefaultBaseView
    template_name = 'knotis/merchant/my_redemptions_view.html'
    post_scripts = [
        'knotis/merchant/js/redemptions.js'
    ]

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
            customer_tile = IdentityTile()
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
        r'^my/customers/$',
    ]

    default_parent_view_class = DefaultBaseView
    template_name = 'knotis/merchant/my_customers.html'

    def process_context(self):
        styles = []
        pre_scripts = []
        post_scripts = []

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
            'styles/default/fileuploader.css'
        ]

        pre_scripts = []

        post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/create.js',
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


class OfferAvailabilityGridView(GridSmallView):
    view_name = 'offer_availability_grid'

    def process_context(self):
        request = self.context.get('request')
        current_identity = None
        if request and request.user.is_authenticated():
            current_identity_id = request.session['current_identity']
            try:
                current_identity = Identity.objects.get(pk=current_identity_id)

            except:
                pass

        page = int(self.context.get('page', '0'))
        count = int(self.context.get('count', '20'))
        start_range = page * count
        end_range = start_range + count

        if (
            current_identity and
            current_identity.identity_type == IdentityTypes.INDIVIDUAL
        ):
            offer_action = 'buy'

        else:
            offer_action = None

        try:
            identity = self.context.get('offer_availability_identity')
            if identity:
                offer_availability = OfferAvailability.objects.filter(
                    identity=identity,
                    available=True
                )[start_range:end_range]

            else:
                offer_availability = None

        except Exception:
            logger.exception(''.join([
                'failed to get offers.'
            ]))

        tiles = []
        for a in offer_availability:
            tile = OfferTile()
            tiles.append(tile.render_template_fragment(Context({
                'offer': a.offer,
                'offer_action': offer_action
            })))
        if not tiles:
            tile = DummyOfferTile()
            tiles = []
            tiles.append(tile.render_template_fragment(Context({
                'identity': identity,
                'current_identity': current_identity,
            })))
        local_context = copy.copy(self.context)
        local_context.update({
            'tiles': tiles
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
        r'^my/offers(/(?P<offer_filter>\w*))?/$',
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


class OfferCreateTile(FragmentView):
    template_name = 'knotis/merchant/create_tile.html'
    view_name = 'offer_edit_tile'


class OfferEditHeaderView(FragmentView):
    template_name = 'knotis/merchant/edit_header.html'
    view_name = 'offer_edit_header'


class OfferEditView(ModalView):
    url_patterns = [
        r'^offer/create/$'
    ]
    template_name = 'knotis/merchant/edit.html'
    view_name = 'offer_edit'
    default_parent_view_class = MyOffersView
    post_scripts = [
        'knotis/wizard/js/wizard.js',
        'knotis/merchant/js/offer_create_wizard.js'
    ]

    def process_context(self):
        self.context['modal_id'] = 'offer-create'

        return super(OfferEditView, self).process_context()


class OfferCreateStepView(WizardStepView):
    wizard_name = 'offer_create'

    def build_query_string(self):
        if not hasattr(self, 'offer') or not self.offer:
            return ''

        return '='.join([
            'id',
            self.offer.id
        ])


class OfferEditProductFormView(OfferCreateStepView):
    template_name = 'knotis/merchant/edit_product_price.html'
    view_name = 'offer_edit_product_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_object_or_404(
            Identity,
            pk=request.session.get('current_identity')
        )

        if IdentityTypes.ESTABLISHMENT != current_identity.identity_type:
            raise PermissionDenied()

        else:
            owner = current_identity

        form = OfferProductPriceForm(
            data=request.POST,
            owners=Identity.objects.filter(pk=owner.pk)
        )

        if not form.is_valid():
            errors = {}
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_ajax_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        offer_id = form.cleaned_data.get('offer_id')
        if offer_id:
            try:
                offer = Offer.objects.get(pk=offer_id)

            except Exception, e:
                logger.exception('failed to get offer')

                return self.generate_ajax_response({
                    'message': 'a server error occurred',
                    'errors': {'no-field': e.message}
                })

        else:
            offer = None

        new_offer = not offer

        product_type = form.cleaned_data.get('product_type')
        if ProductTypes.CREDIT == product_type:
            price = form.cleaned_data.get('credit_price')
            value = form.cleaned_data.get('credit_value')
            title = ''.join([
                '$',
                ('%.2f' % price).rstrip('00').rstrip('.'),
                ' for $',
                ('%.2f' % value).rstrip('00').rstrip('.')
            ])

            try:
                product = Product.objects.get_or_create_credit(
                    price,
                    value
                )

            except Exception, e:
                logger.exception('failed to get or create product')

                return self.generate_ajax_response({
                    'message': 'a server error occurred',
                    'errors': {'no-field': e.message}
                })

        elif ProductTypes.PHYSICAL == product_type:
            price = form.cleaned_data.get('product_price')
            value = form.cleaned_data.get('product_value')
            product_title = form.cleaned_data.get('product_title')
            title = ''.join([
                '$',
                ('%.2f' % price).rstrip('00').rstrip('.'),
                ' for ',
                product_title
            ])

            try:
                product = Product.objects.get_or_create_physical(product_title)

            except Exception, e:
                logger.exception('failed to get or create product')

                return self.generate_ajax_response({
                    'message': 'a server error occurred',
                    'errors': {'no-field': e.message}
                })

        else:
            return HttpResponseServerError(
                'can not create products of this type.'
            )

        owner = form.cleaned_data.get('owner')

        if offer:
            '''
            If there's an existing offer nuke all the offer
            items before manipulating all inventory again.
            '''
            OfferItem.objects.clear_offer_items(offer)

        try:
            inventory = Inventory.objects.create_stack_from_product(
                owner,
                product,
                price=value,
                unlimited=True,
                get_existing=True
            )

        except Exception, e:
            logger.exception('failed to create inventory')

            return self.generate_ajax_response({
                'message': 'a server error occurred',
                'errors': {'no-field': e.message}
            })

        try:
            split_inventory = Inventory.objects.split(
                inventory,
                owner,
                1
            )

        except Exception, e:
            logger.exception('failed to split inventory')

            return self.generate_ajax_response({
                'message': 'a server error occurred',
                'errors': {'no-field': e.message}
            })

        unlimited = form.cleaned_data.get('offer_unlimited', False)
        if unlimited:
            stock = None

        else:
            stock = form.cleaned_data.get('offer_stock')

        if offer:
            try:
                offer.update(
                    title=title,
                    stock=stock,
                    unlimited=unlimited,
                    inventory=[split_inventory],
                    discount_factor=price / value
                )

            except Exception, e:
                logger.exception('failed to update offer')

                return self.generate_ajax_response({
                    'message': 'a server error occurred',
                    'errors': {'no-field': e.message}
                })

        else:
            try:
                offer = Offer.objects.create(
                    owner=owner,
                    title=title,
                    stock=stock,
                    unlimited=unlimited,
                    inventory=[split_inventory],
                    discount_factor=price / value
                )

            except Exception, e:
                logger.exception('failed to create offer')

                return self.generate_ajax_response({
                    'message': 'a server error occurred',
                    'errors': {'no-field': e.message}
                })

        self.offer = offer

        try:
            self.advance('' if new_offer else None)

        except:
            logger.exception('could not advance wizard progress')

        return self.generate_ajax_response({
            'message': 'OK',
            'offer_id': offer.id,
            'wizard_query': self.build_query_string()
        })

    def process_context(self):
        request = self.context.get('request')
        current_identity = get_object_or_404(
            Identity,
            pk=request.session['current_identity']
        )

        if IdentityTypes.ESTABLISHMENT != current_identity.identity_type:
            raise PermissionDenied()

        else:
            owner = current_identity

        offer_id = request.GET.get('id')
        if offer_id:
            self.offer = get_object_or_404(
                Offer,
                pk=offer_id
            )

        else:
            self.offer = None

        local_context = copy.copy(self.context)
        local_context.update({
            'form': OfferProductPriceForm(
                owners=Identity.objects.filter(pk=owner.pk),
                offer=self.offer
            ),
            'ProductTypes': ProductTypes,
            'current_identity': current_identity
        })

        return local_context


class OfferEditDetailsFormView(OfferCreateStepView):
    template_name = 'knotis/merchant/edit_details.html'
    view_name = 'offer_edit_details_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        offer_id = request.POST.get('id')
        offer = get_object_or_404(Offer, pk=offer_id)

        form = OfferDetailsForm(
            data=request.POST,
            instance=offer
        )
        if not form.is_valid():
            errors = {}
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_ajax_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        try:
            self.offer = form.save()

        except Exception, e:
            logger.exception('error while saving offer detail form')
            return self.generate_ajax_response({
                'message': e.message,
                'errors': {
                    'no-field': 'A server error occurred. Please try again.'
                }
            })

        try:
            self.advance()

        except:
            logger.exception('could not advance wizard progress')

        return self.generate_ajax_response({
            'message': 'OK',
            'offer_id': offer.id
        })

    def process_context(self):
        request = self.request
        offer_id = request.GET.get('id')
        self.offer = get_object_or_404(Offer, pk=offer_id)

        local_context = copy.copy(self.context)
        local_context.update({
            'form': OfferDetailsForm(
                instance=self.offer
            ),
        })

        return local_context


class OfferEditLocationFormView(OfferCreateStepView):
    template_name = 'knotis/merchant/edit_photos_location.html'
    view_name = 'offer_edit_location_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity_id = request.session.get('current_identity')
        current_identity = Identity.objects.get(id=current_identity_id)

        offer_id = request.POST.get('offer')
        offer = get_object_or_404(Offer, pk=offer_id)

        photos = ImageInstance.objects.filter(
            owner=current_identity,
            context='offer_banner'
        )

        location_items = LocationItem.objects.filter(
            related_object_id=current_identity_id
        )
        location_ids = [
            location.location_id for location in location_items
        ]
        locations = Location.objects.filter(**{
            'pk__in': location_ids
        })

        form = OfferPhotoLocationForm(
            data=request.POST,
            offer=offer,
            photos=photos,
            locations=locations
        )

        if not form.is_valid():
            errors = {}
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_ajax_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        try:
            self.offer = form.cleaned_data['offer']
            self.offer.default_image = form.cleaned_data['photo']
            self.offer.save()

            locations = form.cleaned_data['locations']
            for location in locations:
                LocationItem.objects.create(
                    location=location,
                    related=offer
                )

        except Exception, e:
            logger.exception('error while saving offer detail form')
            return self.generate_ajax_response({
                'message': e.message,
                'errors': {
                    'no-field': 'A server error occurred. Please try again.'
                }
            })

        try:
            self.advance()

        except:
            logger.exception('could not advance wizard progress')

        return self.generate_ajax_response({
            'message': 'OK',
            'offer_id': self.offer.id
        })

    def process_context(self):
        request = self.context.get('request')
        current_identity_id = request.session.get('current_identity')
        current_identity = Identity.objects.get(id=current_identity_id)

        offer_id = request.GET.get('id')
        self.offer = get_object_or_404(Offer, pk=offer_id)

        photos = ImageInstance.objects.filter(
            owner=current_identity,
            context='offer_banner'
        )

        location_items = LocationItem.objects.filter(
            related_object_id=current_identity_id
        )
        location_ids = [
            location.location_id for location in location_items
        ]
        locations = Location.objects.filter(**{
            'pk__in': location_ids
        })

        local_context = copy.copy(self.context)
        local_context.update({
            'form': OfferPhotoLocationForm(
                offer=self.offer,
                photos=photos,
                locations=locations,
                parameters=self.context
            )
        })

        return local_context


class OfferEditPublishFormView(OfferCreateStepView):
    template_name = 'knotis/merchant/edit_publish.html'
    view_name = 'offer_edit_publish_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity_id = request.session.get('current_identity')
        current_identity = Identity.objects.get(id=current_identity_id)

        offer_id = request.POST.get('offer')
        offer = get_object_or_404(Offer, pk=offer_id)

        publish_queryset = Endpoint.objects.filter(**{
            'identity': current_identity
        })

        form = OfferPublicationForm(
            data=request.POST,
            offer=offer,
            publish_queryset=publish_queryset
        )

        if not form.is_valid():
            errors = {}
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_ajax_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        try:
            self.offer = form.cleaned_data.get('offer')
            self.offer.start_time = form.cleaned_data.get('start_time')
            self.offer.end_time = form.cleaned_data.get('end_time')
            self.offer.save()

            endpoint_current_identity = Endpoint.objects.get(
                endpoint_type=EndpointTypes.IDENTITY,
                identity=current_identity
            )
            OfferPublish.objects.create(
                endpoint=endpoint_current_identity,
                subject=self.offer,
                publish_now=False
            )
            publish = form.cleaned_data.get('publish')
            if publish:
                for endpoint in publish:
                    OfferPublish.objects.create(
                        endpoint=endpoint,
                        subject=self.offer,
                        publish_now=False
                    )

        except Exception, e:
            logger.exception('error while saving offer publication form')
            return self.generate_ajax_response({
                'message': e.message,
                'errors': {
                    'no-field': 'A server error occurred. Please try again.'
                }
            })

        try:
            self.advance()

        except:
            logger.exception('could not advance wizard progress')

        return self.generate_ajax_response({
            'message': 'OK',
            'offer_id': offer.id
        })

    def process_context(self):
        request = self.context.get('request')
        current_identity_id = request.session.get('current_identity')
        current_identity = Identity.objects.get(id=current_identity_id)

        offer_id = request.GET.get('id')
        self.offer = get_object_or_404(Offer, pk=offer_id)

        publish_queryset = Endpoint.objects.filter(**{
            'identity': current_identity
        })

        local_context = copy.copy(self.context)
        local_context.update({
            'form': OfferPublicationForm(
                offer=self.offer,
                publish_queryset=publish_queryset,
                parameters=self.context
            )
        })

        return local_context


class OfferEditSummaryView(OfferCreateStepView):
    template_name = 'knotis/merchant/edit_summary.html'
    view_name = 'offer_edit_summary'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        offer_id = request.POST.get('id')
        offer = get_object_or_404(Offer, pk=offer_id)

        form = OfferFinishForm(
            data=request.POST,
            instance=offer
        )

        if not form.is_valid():
            errors = {}
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_ajax_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        try:
            self.offer = form.save()

        except Exception, e:
            logger.exception('error while publishing offer')
            return self.generate_ajax_response({
                'message': e.message,
                'errors': {
                    'no-field': 'A server error occurred. Please try again.'
                }
            })

        try:
            self.advance()

        except:
            logger.exception('could not advance wizard progress')

        return self.generate_ajax_response({
            'message': 'OK',
            'offer_id': self.offer.id
        })

    def process_context(self):
        request = self.context.get('request')

        offer_id = request.GET.get('id')
        self.offer = get_object_or_404(Offer, id=offer_id)

        try:
            offer_items = OfferItem.objects.filter(offer=self.offer)

        except Exception:
            logger.exception('failed to get offer items')
            offer_items = None

        estimated_sales_max = 3.
        estimated_sales = min(
            estimated_sales_max,
            self.offer.stock
        ) if not self.offer.unlimited else estimated_sales_max
        revenue_per_offer = 0.
        for item in offer_items:
            revenue_per_offer += item.price_discount

        price_adjusted = revenue_per_offer - (
            revenue_per_offer * (
                settings.KNOTIS_MODE_PERCENT + settings.STRIPE_MODE_PERCENT
            ) + settings.STRIPE_MODE_FLAT
        )

        revenue_customer = price_adjusted
        revenue_total = revenue_customer * estimated_sales
        savings_low = revenue_total * .3
        savings_high = revenue_total * .5

        tile = OfferTile()
        tile_rendered = tile.render_template_fragment(Context({
            'offer': self.offer,
        }))
        local_context = copy.copy(self.context)
        local_context.update({
            'summary_revenue_customer': ''.join([
                '$',
                format_currency(revenue_customer)
            ]),
            'summary_savings': ''.join([
                '$',
                format_currency(savings_low),
                ' - ',
                '$',
                format_currency(savings_high)
            ]),
            'summary_revenue_total': ''.join([
                '$',
                format_currency(revenue_total)
            ]),
            'summary_estimated_sales': str(int(estimated_sales)),
            'offer_finish_form': OfferFinishForm(
                instance=self.offer
            ),
            'offer_tile_preview': tile_rendered
        })

        return local_context


class OfferCreateWizard(WizardView):
    view_name = 'offer_create_wizard'
    wizard_name = 'offer_create'


class EstablishmentProfileView(EmbeddedView):
    view_name = 'establishment_profile'
    url_patterns = [
        r''.join([
            '^id/(?P<identity_id>',
            REGEX_UUID,
            ')/$'
        ]),
        r''.join([
            '^id/(?P<identity_id>',
            REGEX_UUID,
            ')(/(?P<view_name>',
            '\w{1,50}',
            '))?/$'
        ])
    ]
    template_name = 'knotis/merchant/establishment_profile.html'
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'jcrop/js/jquery.Jcrop.js',
        'knotis/layout/js/action_button.js',
        'knotis/identity/js/identity-action.js',
        'scripts/fileuploader.js',
        'scripts/jquery.colorbox.js',
        'scripts/jquery.sickle.js',
        'knotis/merchant/js/profile.js',
        'knotis/merchant/js/update_profile.js',
    ]

    def set_establishment(self):

        identity_id = self.context.get('identity_id')
        identity = Identity.objects.get(pk=identity_id)
        if not identity:
            raise Exception('Identity not found')

        if identity.identity_type == IdentityTypes.ESTABLISHMENT:
            self.establishment_id = identity_id
            self.establishment = identity

        elif identity.identity_type == IdentityTypes.BUSINESS:
            try:
                establishments = (
                    IdentityEstablishment.objects.get_establishments(
                        identity
                    )
                )
            except:
                establishments = None
                logger.exception('Failed to get establishments for business')

            if len(establishments) > 0:
                self.establishment_id = establishments[0].pk
                self.establishment = establishments[0]

            else:
                raise Exception('Business profile not implemented yet.')

        else:
            raise Exception('Identity profile not implemented yet.')

    def is_manager(self):
        request = self.request
        self.is_manager = False
        if request.user.is_authenticated():
            current_identity_id = request.session.get('current_identity')
            current_identity = Identity.objects.get(
                pk=current_identity_id
            )

            self.is_manager = (
                current_identity.is_manager(self.establishment) or
                current_identity.pk == self.establishment.pk
            )

    def set_business(self):
        if not hasattr(self, 'establishment'):
            self.set_establishment()

        try:
            self.business = IdentityBusiness.objects.get_establishment_parent(
                self.establishment
            )

        except:
            logger.exception(
                ' '.join([
                    'failed to get business for establishment with id ',
                    self.establishment_id
                ])
            )
            raise Http404

    def set_images(self):
        if not hasattr(self, 'business'):
            self.set_establishment()

        if self.is_manager:
            self.default_profile_logo_uri = ''.join([
                settings.STATIC_URL,
                'knotis/identity/img/add_logo.png'
            ])

        else:
            self.default_profile_logo_uri = ''.join([
                settings.STATIC_URL,
                'knotis/identity/img/profile_default.png'
            ])

        self.profile_badge_image = get_identity_profile_badge(
            self.establishment
        )
        self.profile_banner_image = get_identity_profile_banner(
            self.establishment
        )
        self.profile_banner_color = get_identity_default_profile_banner_color(
            self.establishment
        )

    def process_context(self):
        # Super user check.
        is_superuser = False
        request = self.request
        if request.user.is_authenticated():
            current_identity_id = request.session.get('current_identity')
            current_identity = Identity.objects.get(pk=current_identity_id)

            if (
                current_identity and
                current_identity.identity_type == IdentityTypes.SUPERUSER
            ):
                is_superuser = True
        else:
            current_identity = None

        self.set_establishment()
        self.set_business()

        self.is_manager()
        self.set_images()

        location_item = LocationItem.objects.filter(
            related_object_id=self.establishment.id
        )
        if len(location_item):
            address = location_item[0].location.address
        else:
            address = None

        endpoints = Endpoint.objects.filter(
            identity=self.establishment,
            primary=True
        )
        endpoints = endpoints.select_subclasses()

        endpoint_dicts = []
        for endpoint_class in (
                EndpointPhone,
                EndpointEmail,
                EndpointFacebook,
                EndpointYelp,
                EndpointTwitter,
                EndpointWebsite
        ):

            endpoint = None
            for ep in endpoints:
                if ep.endpoint_type == endpoint_class.EndpointType:
                    endpoint = ep

            endpoint_type_name = EndpointTypeNames[endpoint_class.EndpointType]
            endpoint_type_name = endpoint_type_name.lower()

            if endpoint and endpoint.value:

                display = None
                if endpoint.endpoint_type == EndpointTypes.YELP:
                    display = 'Yelp'
                elif endpoint.endpoint_type == EndpointTypes.FACEBOOK:
                    display = 'Facebook'

                endpoint_dict = {
                    'id': endpoint.id,
                    'endpoint_type_name': endpoint_type_name,
                    'value': endpoint.value,
                    'uri': endpoint.get_uri(),
                    'display': display,
                    'endpoint_type': endpoint_class.EndpointType
                }

                endpoint_dicts.append(endpoint_dict)

            else:
                endpoint_dicts.append({
                    'id': '',
                    'endpoint_type_name': endpoint_type_name,
                    'value': '',
                    'uri': '',
                    'display': '',
                    'endpoint_type': endpoint_class.EndpointType
                })

        # endpoints displayed on the cover
        phone = None
        website = None
        for endpoint in endpoints:
            if EndpointTypes.PHONE == endpoint.endpoint_type:
                phone = {
                    'value': endpoint.value,
                    'uri': endpoint.get_uri()
                }

            if EndpointTypes.WEBSITE == endpoint.endpoint_type:
                website = {
                    'value': endpoint.value,
                    'uri': endpoint.get_uri(),
                    'display': endpoint.get_display()
                }

            if phone and website:
                break

        # determine nav view
        request = self.request
        context_context = Context({
            'request': request,
            'establishment_id': self.establishment_id,
            'endpoints': endpoint_dicts,
            'is_manager': self.is_manager
        })

        default_view_name = 'about'

        view_name = self.context.get('view_name', default_view_name)

        if view_name == 'contact':
            profile_content = (
                EstablishmentProfileLocation().render_template_fragment(
                    context_context
                )
            )
            content_plexer = 'offersaboutcontact'

        elif view_name == 'offers':
            content_plexer = 'offersaboutcontact'
            context_context['offer_availability_identity'] = self.establishment
            profile_content = (
                OfferAvailabilityGridView().render_template_fragment(
                    context_context
                )
            )

        elif view_name == 'about':
            content_plexer = 'offersaboutcontact'
            profile_content = (
                EstablishmentProfileAbout().render_template_fragment(
                    context_context
                )
            )

        else:
            content_plexer = 'establishments'
            profile_content = 'establishments'

        identity_tile_context = Context({
            'current_identity': current_identity,
            'identity': self.establishment
        })

        if ((current_identity and
                current_identity.identity_type == IdentityTypes.INDIVIDUAL) or
                current_identity is None):
            action_button = IdentityActionButton()
            action_button_content = action_button.render_template_fragment(
                identity_tile_context
            )
        else:
            action_button_content = None

        local_context = copy.copy(self.context)
        local_context.update({
            'establishment': self.establishment,
            'is_manager': self.is_manager,
            'address': address,
            'phone': phone,
            'website': website,
            'business': self.business,
            'default_profile_logo_uri': self.default_profile_logo_uri,
            'profile_badge': self.profile_badge_image,
            'profile_banner': self.profile_banner_image,
            'profile_banner_color': self.profile_banner_color,
            'top_menu_name': 'identity_profile',
            'profile_content': profile_content,
            'view_name': view_name,
            'content_plexer': content_plexer,
            'action_button': action_button_content,
            'is_superuser': is_superuser,
        })

        return local_context


class EstablishmentProfileLocation(FragmentView):
    template_name = 'knotis/merchant/establishment_about_location.html'
    view_name = 'establishment_location'

    def process_context(self):
        establishment_id = self.context.get('establishment_id')
        endpoints = self.context.get('endpoints')

        local_context = copy.copy(self.context)
        phone = website = None
        for endpoint in endpoints:
            if (
                endpoint['endpoint_type'] == EndpointTypes.PHONE and
                endpoint['value']
            ):
                phone = endpoint

            elif (
                endpoint['endpoint_type'] == EndpointTypes.WEBSITE and
                endpoint['value']
            ):
                website = endpoint

        location_item = LocationItem.objects.filter(
            related_object_id=establishment_id
        )
        if len(location_item):
            address = location_item[0].location.address
            latitude = location_item[0].location.latitude
            longitude = location_item[0].location.longitude
        else:
            address = None
            latitude = None
            longitude = None

        local_context.update({
            'address': address,
            'phone': phone,
            'website': website,
            'latitude': latitude,
            'longitude': longitude
        })
        return local_context


class EstablishmentAboutDetails(AJAXFragmentView):
    template_name = 'knotis/merchant/establishment_about_details.html'
    view_name = 'establishment_about_details'

    def process_context(self):
        has_data = False
        establishment_id = self.context.get('establishment_id')

        establishment = IdentityEstablishment.objects.get(pk=establishment_id)

        local_context = copy.copy(self.context)
        local_context.update({
            'description': establishment.description
        })

        if establishment.description:
            has_data = True

        # Fetch and add the address and coordinates to local_context
        location_item = LocationItem.objects.filter(
            related_object_id=establishment.pk
        )
        if len(location_item):
            address = location_item[0].location.address
            address_latitude = location_item[0].location.latitude,
            address_longitude = location_item[0].location.longitude
        else:
            address = None
            address_latitude = None
            address_longitude = None

        local_context.update({
            'address': address,
            'address_latitude': address_latitude,
            'address_longitude': address_longitude
        })

        # add business name to local_context
        local_context.update({
            'STATIC_URL': settings.STATIC_URL,
            'establishment': establishment
        })

        # add contact info (endpoints) to local_context
        endpoints = self.context.get('endpoints')
        for endpoint in endpoints:
            endpoint_type_name = endpoint['endpoint_type_name']
            local_context.update({
                endpoint_type_name: {
                    'value': endpoint['value'],
                    'id': endpoint['id'],
                    'endpoint_type': endpoint['endpoint_type'],
                    'display': endpoint['display'],
                    'uri': endpoint['uri']
                }
            })
            if (
                endpoint['value'] and (
                    endpoint_type_name == 'facebook'
                    or endpoint_type_name == 'yelp'
                    or endpoint_type_name == 'twitter'
                )
            ):
                has_data = True

        local_context['has_data'] = has_data

        return local_context

    def post(
            self,
            request,
            *args,
            **kwargs
    ):

        data = json.loads(request.POST.get('data'))
        establishment_id = data['establishment_id']
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)

        # business name
        response = {}
        response['establishment_id'] = establishment_id
        if 'changed_name' in data:
            establishment.name = data['changed_name']

        if 'changed_description' in data:
            establishment.description = data['changed_description']

        establishment.save()

        # endpoints
        def endpoint_to_dict(endpoint):
            sendable = {
                'pk': endpoint.pk,
                'endpoint_type': endpoint.endpoint_type,
                'value': endpoint.value,
                'url': endpoint.get_uri()
            }

            return sendable

        updated_endpoints = []
        deleted_endpoints = []
        if 'changed_endpoints' in data:
            for endpoint_name in data['changed_endpoints'].keys():
                endpoint = data['changed_endpoints'][endpoint_name]
                endpoint_id = endpoint['endpoint_id']

                endpoint_value = endpoint['endpoint_value'].strip()

                updated_endpoint = Endpoint.objects.update_or_create(
                    identity=establishment,
                    pk=endpoint_id,
                    endpoint_type=int(endpoint['endpoint_type']),
                    value=endpoint_value,
                    primary=True
                )

                if updated_endpoint.deleted:
                    deleted_endpoints.append(updated_endpoint)
                else:
                    updated_endpoints.append(updated_endpoint)

        return self.generate_ajax_response({
            'status': 'ok',
            'updated_endpoints': map(endpoint_to_dict, updated_endpoints),
            'deleted_endpoints': map(endpoint_to_dict, deleted_endpoints)
        })


class EstablishmentAboutTwitterFeed(FragmentView):
    template_name = 'knotis/merchant/establishment_about_twitter.html'
    view_name = 'establishment_about_twitter'

    def process_context(self):
        local_context = copy.copy(self.context)

        endpoints = self.context.get('endpoints')
        twitter_endpoint = None
        for endpoint in endpoints:
            if endpoint['endpoint_type_name'] == 'twitter':
                if endpoint['value']:
                    twitter_endpoint = endpoint
                    local_context.update({
                        'twitter_handle': twitter_endpoint['value'],
                        'twitter': twitter_endpoint,
                    })

        twitter_feed = None
        self.has_feed = False
        if(twitter_endpoint):
            feed_json = get_twitter_feed_json(twitter_endpoint['value'])
            if feed_json:
                twitter_feed = json.loads(feed_json)
                self.has_feed = len(twitter_feed) > 0
                local_context.update({
                    'twitter_feed': twitter_feed
                })

        return local_context


class EstablishmentAboutYelpFeed(FragmentView):
    template_name = 'knotis/merchant/establishment_about_yelp.html'
    view_name = 'establishment_about_yelp'

    def process_context(self):
        endpoints = self.context.get('endpoints')
        yelp_endpoint = None

        for endpoint in endpoints:
            if endpoint['endpoint_type_name'] == 'yelp':
                if endpoint['value']:
                    yelp_endpoint = endpoint

        yelp_feed = None
        self.has_feed = False
        if yelp_endpoint:
            yelp_feed = get_reviews_by_yelp_id(yelp_endpoint['value'])

            self.has_feed = len(yelp_feed)

        local_context = copy.copy(self.context)
        local_context.update({
            'yelp_feed': yelp_feed,
            'yelp': yelp_endpoint
        })

        return local_context


class EstablishmentAboutFeeds(FragmentView):
    template_name = 'knotis/merchant/establishment_about_feeds.html'
    view_name = 'establishment_about_feeds'

    def process_context(self):
        local_context = copy.copy(self.context)

        yelp = EstablishmentAboutYelpFeed()
        twitter = EstablishmentAboutTwitterFeed()

        local_context.update({
            'yelp_markup': yelp.render_template_fragment(local_context),
            'yelp_has_feed': yelp.has_feed,

            'twitter_markup': twitter.render_template_fragment(local_context),
            'twitter_has_feed': twitter.has_feed
        })

        return local_context


class EstablishmentAboutCarousel(FragmentView):
    template_name = 'knotis/merchant/establishment_about_carousel.html'
    view_name = 'establishment_about_carousel'

    def process_context(self):
        establishment_id = self.context.get('establishment_id')
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)

        images = ImageInstance.objects.filter(
            related_object_id=establishment.pk,
            context='business_profile_carousel'
        )

        image_infos = []
        for count, image in enumerate(images):
            image_infos.append((count, image))

        local_context = copy.copy(self.context)
        local_context.update({
            'images': image_infos,
        })

        return local_context


class EstablishmentProfileAbout(FragmentView):
    template_name = 'knotis/merchant/establishment_about.html'
    view_name = 'establishment_about'

    def process_context(self):
        local_context = copy.copy(self.context)
        sections = []

        about = EstablishmentAboutDetails()
        about_markup = about.render_template_fragment(local_context)
        about_markup = about_markup.strip()
        if about_markup:
            sections.append({
                'markup': about_markup,
            })

        carousel = EstablishmentAboutCarousel()
        carousel_markup = carousel.render_template_fragment(local_context)
        carousel_markup = carousel_markup.strip()
        if carousel_markup:
            sections.append({
                'markup': carousel_markup,
            })

        feeds = EstablishmentAboutFeeds()
        feeds_markup = feeds.render_template_fragment(local_context)
        feeds_markup = feeds_markup.strip()
        if feeds_markup:
            sections.append({
                'markup': feeds_markup,
            })

        location = EstablishmentProfileLocation()
        location_markup = location.render_template_fragment(local_context)
        location_markup = location_markup.strip()
        if location_markup:
            sections.append({
                'markup': location_markup,
            })

        local_context.update({
            'sections': sections,
        })
        return local_context

get_class = lambda x: globals()[x]


class BusinessProfileView(FragmentView):
    template_name = 'knotis/merchant/profile_business.html'
    view_name = 'business_profile'

    def process_context(self):
        pass


class CreateBusinessView(ModalView, GetCurrentIdentityMixin):
    url_patterns = [
        r'^identity/business/create/$'
    ]
    template_name = 'knotis/merchant/business_create.html'
    view_name = 'business_create'
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'knotis/merchant/js/business_create.js'
    ]

    def process_context(self):
        self.context['modal_id'] = 'business-create'
        return self.context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        current_identity = self.get_current_identity(request)
        if (
            IdentityTypes.BUSINESS == current_identity.identity_type or
            IdentityTypes.ESTABLISHMENT == current_identity.identity_type
        ):
            errors['no-field'] = (
                'This type of identity cannot create businesses.'
            )

        name = request.POST.get('name')
        if not name:
            errors['fields'] = {
                'name': 'Name is required to create a business.'
            }

        if not errors:
            try:
                business, establishment = IdentityApi.create_business(
                    current_identity.pk,
                    name=name
                )

                data['business_pk'] = business.pk
                data['establishment_pk'] = establishment.pk

            except Exception, e:
                logger.exception(e.message)
                errors['exception'] = e.message

            try:
                user_information = UserInformation.objects.get(
                    user=request.user
                )
                user_information.default_identity_id = establishment.pk
                user_information.save()
                request.session['current_identity'] = establishment.pk

            except Exception, e:
                logger.exception(e.message)

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )
