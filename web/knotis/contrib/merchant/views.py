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

from knotis.contrib.layout.views import (
    GridSmallView,
    DefaultBaseView,
)

from knotis.views import (
    ContextView,
    FragmentView,
    EmbeddedView,
    ModalView,
    GenerateAjaxResponseMixin
)

from knotis.contrib.media.models import ImageInstance
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes,
    IdentityIndividual,
    IdentityEstablishment,
    IdentityBusiness
)

from knotis.contrib.offer.models import (
    Offer,
    OfferItem,
    OfferTypes,
    OfferPublish
)

from knotis.contrib.offer.views import OfferTile

from knotis.contrib.wizard.views import (
    WizardView,
    WizardStepView
)
from knotis.contrib.identity.views import (
    IdentityTile,
    TransactionTileView
)

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
        r'/create/$'
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

        if IdentityTypes.ESTABLISHMENT == current_identity.identity_type:
            owner = IdentityBusiness.objects.get_establishment_parent(
                current_identity
            )

        elif IdentityTypes.BUSINESS == current_identity.identity_type:
            owner = current_identity

        else:
            raise PermissionDenied()

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
