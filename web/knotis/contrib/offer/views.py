import copy

from django.shortcuts import (
    render,
    get_object_or_404
)
from django.core.exceptions import (
    ValidationError,
    PermissionDenied
)
from django.http import (
    HttpResponseServerError
)
from django.template import Context
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.utils.view import format_currency

from knotis.contrib.offer.models import (
    Offer,
    OfferItem,
    OfferPublish
)
from knotis.contrib.product.models import (
    Product,
    ProductTypes
)
from knotis.contrib.inventory.models import (
    Inventory
)
from knotis.contrib.media.models import Image
from knotis.contrib.location.models import (
    Location,
    LocationItem
)

from knotis.contrib.identity.models import Identity

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)

from knotis.views import (
    ContextView,
    FragmentView,
    AJAXFragmentView
)

from forms import (
    OfferProductPriceForm,
    OfferDetailsForm,
    OfferPhotoLocationForm,
    OfferPublicationForm,
    OfferFinishForm
)

from knotis.contrib.wizard.views import(
    WizardView,
    WizardStep
)


class OffersView(ContextView):
    template_name = 'knotis/offer/offers_view.html'

    def process_context(self):
        return self.context


class OfferPurchaseView(ContextView):
    template_name = 'knotis/offer/offer_purchase_view.html'

    def process_context(self):
        return self.context


class OfferTile(FragmentView):
    template_name = 'knotis/offer/tile.html'
    view_name = 'offer_tile'
    offer_stats = 'osdfisdjf'

    def process_context(self):
        offer = self.context.get('offer', None)

        if not offer:
            return self.context

        # TODO: CALCULATE STATS.
        self.context.update({
            'stats': 'Stats',
        })

        return self.context


class OfferCreateTile(FragmentView):
    template_name = 'knotis/offer/create_tile.html'
    view_name = 'offer_edit_tile'


class OfferEditHeaderView(FragmentView):
    template_name = 'knotis/offer/edit_header.html'
    view_name = 'offer_edit_header'


class OfferEditView(ContextView):
    template_name = 'knotis/offer/edit.html'
    view_name = 'offer_edit'


class OfferEditProductFormView(AJAXFragmentView):
    template_name = 'knotis/offer/edit_product_price.html'
    view_name = 'offer_edit_product_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_object_or_404(
            Identity,
            pk=request.session.get('current_identity_id')
        )

        form = OfferProductPriceForm(
            data=request.POST,
            owners=Identity.objects.filter(pk=current_identity.pk)
        )

        if not form.is_valid():
            errors = {}
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

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

                return self.generate_response({
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

                return self.generate_response({
                    'message': 'a server error occurred',
                    'errors': {'no-field': e.message}
                })

        else:
            return HttpResponseServerError(
                'can not create products of this type.'
            )

        owner = form.cleaned_data.get('owner')

        try:
            inventory = Inventory.objects.create_stack_from_product(
                owner,
                product,
                value
            )

        except Exception, e:
            logger.exception('failed to create inventory')

            return self.generate_response({
                'message': 'a server error occurred',
                'errors': {'no-field': e.message}
            })

        unlimited = form.cleaned_data.get('offer_unlimited', False)
        if unlimited:
            stock = None

        else:
            stock = form.cleaned_data.get('offer_stock')

        try:
            offer = Offer.objects.create(
                owner=owner,
                title=title,
                stock=stock,
                unlimited=unlimited,
                inventory=[inventory],
                discount_factor=price / value
            )

        except Exception, e:
            logger.exception('failed to create offer')

            return self.generate_response({
                'message': 'a server error occurred',
                'errors': {'no-field': e.message}
            })

        return self.generate_response({
            'message': 'OK',
            'offer_id': offer.id
        })

    def process_context(self):
        request = self.context.get('request')
        current_identity = get_object_or_404(
            Identity,
            pk=request.session['current_identity_id']
        )

        local_context = copy.copy(self.context)
        local_context.update({
            'form': OfferProductPriceForm(
                owners=Identity.objects.filter(pk=current_identity.pk)
            ),
            'ProductTypes': ProductTypes,
            'current_identity': current_identity
        })

        return local_context


class OfferEditDetailsFormView(AJAXFragmentView):
    template_name = 'knotis/offer/edit_details.html'
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

            return self.generate_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        try:
            offer = form.save()

        except Exception, e:
            logger.exception('error while saving offer detail form')
            return self.generate_response({
                'message': e.message,
                'errors': {
                    'no-field': 'A server error occurred. Please try again.'
                }
            })

        return self.generate_response({
            'message': 'OK',
            'offer_id': offer.id
        })

    def process_context(self):
        offer = None

        request = self.request
        offer_id = request.GET.get('id')
        offer = get_object_or_404(Offer, pk=offer_id)

        local_context = copy.copy(self.context)
        local_context.update({
            'form': OfferDetailsForm(
                instance=offer
            ),
        })

        return local_context


class OfferEditLocationFormView(AJAXFragmentView):
    template_name = 'knotis/offer/edit_photos_location.html'
    view_name = 'offer_edit_location_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity_id = request.session.get('current_identity_id')
        current_identity = Identity.objects.get(id=current_identity_id)

        offer_id = request.POST.get('offer')
        offer = get_object_or_404(Offer, pk=offer_id)

        photos = Image.objects.filter(
            owner=current_identity
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

            return self.generate_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        try:
            offer = form.cleaned_data['offer']
            offer.default_image = form.cleaned_data['photo']
            offer.save()

            locations = form.cleaned_data['locations']
            for location in locations:
                LocationItem.objects.create(
                    location=location,
                    related=offer
                )

        except Exception, e:
            logger.exception('error while saving offer detail form')
            return self.generate_response({
                'message': e.message,
                'errors': {
                    'no-field': 'A server error occurred. Please try again.'
                }
            })

        return self.generate_response({
            'message': 'OK',
            'offer_id': offer.id
        })

    def process_context(self):
        request = self.context.get('request')
        current_identity_id = request.session.get('current_identity_id')
        current_identity = Identity.objects.get(id=current_identity_id)

        offer_id = request.GET.get('id')
        offer = get_object_or_404(Offer, pk=offer_id)

        photos = Image.objects.filter(
            owner=current_identity
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
                offer=offer,
                photos=photos,
                locations=locations
            )
        })

        return local_context


class OfferEditPublishFormView(AJAXFragmentView):
    template_name = 'knotis/offer/edit_publish.html'
    view_name = 'offer_edit_publish_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity_id = request.session.get('current_identity_id')
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

            return self.generate_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        try:
            offer = form.cleaned_data.get('offer')
            offer.start_time = form.cleaned_data.get('start_time')
            offer.end_time = form.cleaned_data.get('end_time')
            offer.save()

            endpoint_current_identity = Endpoint.objects.get(
                endpoint_type=EndpointTypes.IDENTITY,
                identity=current_identity
            )
            OfferPublish.objects.create(
                endpoint=endpoint_current_identity,
                subject=offer
            )
            publish = form.cleaned_data.get('publish')
            if publish:
                for endpoint in publish:
                    OfferPublish.objects.create(
                        endpoint=endpoint,
                        subject=offer
                    )

        except Exception, e:
            logger.exception('error while saving offer publication form')
            return self.generate_response({
                'message': e.message,
                'errors': {
                    'no-field': 'A server error occurred. Please try again.'
                }
            })

        return self.generate_response({
            'message': 'OK',
            'offer_id': offer.id
        })

    def process_context(self):
        request = self.context.get('request')
        current_identity_id = request.session.get('current_identity_id')
        current_identity = Identity.objects.get(id=current_identity_id)

        offer_id = request.GET.get('id')
        offer = get_object_or_404(Offer, pk=offer_id)

        publish_queryset = Endpoint.objects.filter(**{
            'identity': current_identity
        })

        local_context = copy.copy(self.context)
        local_context.update({
            'form': OfferPublicationForm(
                offer=offer,
                publish_queryset=publish_queryset
            )
        })

        return local_context


class OfferEditSummaryView(AJAXFragmentView):
    template_name = 'knotis/offer/edit_summary.html'
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

            return self.generate_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        try:
            offer = form.save()

        except Exception, e:
            logger.exception('error while publishing offer')
            return self.generate_response({
                'message': e.message,
                'errors': {
                    'no-field': 'A server error occurred. Please try again.'
                }
            })

        return self.generate_response({
            'message': 'OK',
            'offer_id': offer.id
        })

    def process_context(self):
        request = self.context.get('request')

        offer_id = request.GET.get('id')
        offer = get_object_or_404(Offer, id=offer_id)

        try:
            offer_items = OfferItem.objects.filter(offer=offer)

        except Exception:
            logger.exception('failed to get offer items')
            offer_items = None

        # FIXME: These two parameters should call
        # methods that figure these numbers out.
        knotis_cut = .035
        estimated_sales_max = 3.

        estimated_sales = min(
            estimated_sales_max,
            offer.stock
        ) if not offer.unlimited else estimated_sales_max
        revenue_per_offer = 0.
        for item in offer_items:
            revenue_per_offer += item.price_discount

        revenue_customer = revenue_per_offer - knotis_cut * revenue_per_offer
        revenue_total = revenue_customer * estimated_sales
        savings_low = revenue_total * .3
        savings_high = revenue_total * .5

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
                instance=offer
            )
        })

        return local_context


class OfferGridSmall(FragmentView):
    template_name = 'knotis/layout/grid_small.html'
    view_name = 'offer_small'


class OfferDetailView(AJAXFragmentView):
    template_name = 'knotis/offer/detail.html'
    view_name = 'offer_detail'

    def process_context(self):
        offer_id = self.context.get('kwargs', {}).get('offer_id')
        #request.GET.get('offer_id')
        offer = get_object_or_404(Offer, id=offer_id)

        try:
            offer_items = OfferItem.objects.filter(offer=offer)

        except Exception:
            logger.exception('failed to get offer items')
            offer_items = None

        local_context = copy.copy(self.context)
        local_context.update({
            'offer': offer,
            'offer_items': offer_items
        })

        return local_context


class OfferCreateWizard(WizardView):
    view_name = 'offer_create_wizard'

    steps = [
        WizardStep(
            '/offer/create/product/',
            'offer-edit-product-form',
            {}
        ),
        WizardStep(
            '/offer/create/details/',
            'offer-edit-details-form',
            {'id': 'offer_id'}
        ),
        WizardStep(
            '/offer/create/location/',
            'offer-edit-location-form',
            {'id': 'offer_id'}
        ),
        WizardStep(
            '/offer/create/publish/',
            'offer-edit-publish-form',
            {'id': 'offer_id'}
        ),
        WizardStep(
            '/offer/create/summary/',
            'offer-edit-summary',
            {'id': 'offer_id'}
        ),
    ]
