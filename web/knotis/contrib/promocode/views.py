from django.shortcuts import get_object_or_404, redirect

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

        if request.user.is_authenticated():
            current_identity = self.get_current_identity(request)
        else:
            current_identity = None

        url, _ = PromoCodeApi.execute_promo_code(
            request,
            current_identity,
            promo_code
        )

        return redirect(url)


class ActivateView(PromoCodeView):
    url_patterns = [
        r''.join([
            '^activate/$'
        ]),
    ]

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return redirect('/promo/')


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

        url, _ = PromoCodeApi.execute_promo_code(
            request,
            current_identity,
            promo_code
        )

        return redirect(url)
