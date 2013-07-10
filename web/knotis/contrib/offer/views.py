import random
import string

from django.conf import settings
from django.shortcuts import (
    render,
    redirect
)
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.template import Context
from django.forms import (
    ModelForm,
    CharField,
    DateTimeField,
    ValidationError
)
from django.utils.http import urlquote
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.utils.view import (
    get_standard_template_parameters,
    get_boolean_from_request
)
from knotis.utils.email import generate_email
from knotis.contrib.offer.models import (
    Offer,
    OfferSort
)
from knotis.contrib.product.models import (
    Product,
    ProductTypes
)
from knotis.contrib.inventory.models import (
    Inventory
)

from knotis.contrib.transaction.models import (
    Transaction,
    TransactionTypes
)
from knotis.contrib.identity.models import (
    Identity,
    IdentityBusiness,
    IdentityTypes
)
from knotis.contrib.media.models import Image
from knotis.contrib.media.views import render_image_list
from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.paypal.views import (
    generate_ipn_hash,
    render_paypal_button
)
from knotis.contrib.maps.views import OfferMap

from knotis.views import (
    FragmentView,
    AJAXFragmentView
)

from forms import (
    OfferProductPriceForm,
    OfferDetailsForm,
    OfferPhotoLocationForm,
    OfferPublicationForm
)


class OfferTile(FragmentView):
    template_name = 'knotis/offer/tile.html'
    view_name = 'offer_tile'


class OfferCreateTile(FragmentView):
    template_name = 'knotis/offer/create_tile.html'
    view_name = 'offer_edit_tile'


class OfferEditHeaderView(FragmentView):
    template_name = 'knotis/offer/edit_header.html'
    view_name = 'offer_edit_header'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            OfferEditHeaderView,
            cls
        ).render_template_fragment(context)


class OfferEditView(FragmentView):
    template_name = 'knotis/offer/edit.html'
    view_name = 'offer_edit'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        template_parameters = {
        }

        return render(
            request,
            self.template_name,
            template_parameters
        )


class OfferEditProductFormView(AJAXFragmentView):
    template_name = 'knotis/offer/edit_product_price.html'
    view_name = 'offer_edit_product_form'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return self.render_ajax_fragment(request)

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        try:
            current_identity = Identity.objects.get(
                id=request.session['current_identity_id']
            )

        except:
            current_identity = None

        if not current_identity:
            return HttpResponseNotFound()

        if current_identity.identity_type != IdentityTypes.BUSINESS:
            return HttpResponseServerError()

        form = OfferProductPriceForm(
            owners=IdentityBusiness.objects.filter(
                pk=current_identity.id
            ),
            data=request.POST
        )

        if not form.is_valid():
            errors = {}
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })

        import pdb; pdb.set_trace()

        product_type = form.cleaned_data.get('product_type')
        if ProductTypes.CREDIT == product_type:
            price = form.cleaned_data.get('credit_price')
            value = form.cleaned_data.get('credit_value')
            title = ''.join([
                '$',
                price,
                ' for $',
                value
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
            title = ''.join(
                '$',
                price,
                ' for ',
                product_title
            )

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

        unlimited = form.cleaned_data.get('unlimited', False)
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

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        request = context.get('request')
        try:
            current_identity = Identity.objects.get(
                id=request.session['current_identity_id']
            )

        except:
            current_identity = None

        local_context = Context(context.dicts)
        local_context.update({
            'form': OfferProductPriceForm(
                owners=IdentityBusiness.objects.filter(
                    pk=current_identity.id
                )
            ),
            'ProductTypes': ProductTypes,
            'current_identity': current_identity
        })

        return super(
            OfferEditProductFormView,
            cls
        ).render_template_fragment(local_context)


class OfferEditDetailsFormView(FragmentView):
    template_name = 'knotis/offer/edit_details.html'
    view_name = 'offer_edit_details_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(
            OfferEditDetailsFormView,
            self,
        ).post(
            request,
            *args,
            **kwargs
        )

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            OfferEditDetailsFormView,
            cls
        ).render_template_fragment(context)


class OfferEditLocationFormView(FragmentView):
    template_name = 'knotis/offer/edit_location.html'
    view_name = 'offer_edit_location_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(
            OfferEditLocationFormView,
            self,
        ).post(
            request,
            *args,
            **kwargs
        )

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            OfferEditLocationFormView,
            cls
        ).render_template_fragment(context)


class OfferEditPublishFormView(FragmentView):
    template_name = 'knotis/offer/edit_publish.html'
    view_name = 'offer_edit_publish_form'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(
            OfferEditPublishFormView,
            self,
        ).post(
            request,
            *args,
            **kwargs
        )

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            OfferEditPublishFormView,
            cls
        ).render_template_fragment(context)


class OfferEditSummaryView(FragmentView):
    template_name = 'knotis/offer/edit_summary.html'
    view_name = 'offer_edit_summary'


class OfferGridSmall(FragmentView):
    template_name = 'knotis/layout/grid_small.html'
    view_name = 'offer_small'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            OfferGridSmall,
            cls
        ).render_template_fragment(context)
