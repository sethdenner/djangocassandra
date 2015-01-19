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
from knotis.contrib.promocode.models import PromoCode


class PromoCodeView(EmbeddedView, GetCurrentIdentityMixin):
    template_name = 'knotis/promo_code/form.html'
    url_patterns = [
        r''.join([
            '^promo/$'
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

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        self.response_format = self.RESPONSE_FORMATS.REDIRECT
        promo_code_value = request.POST.get('promo_code').lower()

        promo_code = get_object_or_404(
            PromoCode,
            value=promo_code_value
        )
        current_identity = self.get_current_identity(request)

        _, exec_func = PromoCodeApi.execute_promo_code(
            request,
            current_identity,
            promo_code
        )
        exec_func()

        data = {
            'next': '/my/purchases/'
        }
        errors = {}

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )


class PromoCodeRedirectView(PromoCodeView):
    url_patterns = [
        r''.join([
            '^promo'
            '/(?P<promo_code>',
            REGEX_PROMO,
            ')/$'
        ]),
    ]

    def get(
        self,
        request,
        promo_code,
        *args,
        **kwargs
    ):

        promo_code_value = promo_code.lower()
        promo_code = get_object_or_404(
            PromoCode,
            value=promo_code_value
        )
        current_identity = self.get_current_identity(request)

        url, _  = PromoCodeApi.execute_promo_code(
            request,
            current_identity,
            promo_code
        )

        return redirect(url)
