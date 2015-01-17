from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect

from knotis.contrib.transaction.models import (
    TransactionCollection
)

from knotis.views import (
    EmbeddedView,
)
from knotis.utils.regex import REGEX_PROMO

from knotis.contrib.layout.views import (
    DefaultBaseView,
)

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.promocode.api import PromoCodeApi
from knotis.contrib.promocode.models import ConnectPromoCode


class PromoCodeView(EmbeddedView, GetCurrentIdentityMixin):
    template_name = 'knotis/promo_code/form.html'
    url_patterns = [
        r''.join([
            '^promo'
            '(/(?P<promo_code>',
            REGEX_PROMO,
            '))?/$'
        ]),
    ]
    default_parent_view_class = DefaultBaseView
    styles = [
        'knotis/promocode/css/promo_code_form.css',
    ]

    @method_decorator(login_required)
    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(PromoCodeView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get(
        self,
        request,
        promo_code,
        *args,
        **kwargs
    ):

        promo_code_value = promo_code.lower()
        promo_code = get_object_or_404(
            ConnectPromoCode,
            value=promo_code_value
        )

        transaction_collection = TransactionCollection.objects.get(
            pk=promo_code.context
        )

        return redirect('/qrcode/connect/%s/' % transaction_collection.pk)

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        self.response_format = self.RESPONSE_FORMATS.REDIRECT
        promo_code_value = request.POST.get('promo_code').lower()

        promo_code = get_object_or_404(
            ConnectPromoCode,
            value=promo_code_value
        )
        current_identity = self.get_current_identity(request)

        PromoCodeApi.connect_offer_collection(
            request,
            current_identity,
            promo_code
        )

        data = {
            'next': '/my/purchases/'
        }
        errors = {}

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )
