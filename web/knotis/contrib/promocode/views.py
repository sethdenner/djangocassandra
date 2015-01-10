from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from knotis.views import (
    EmbeddedView,
)
from knotis.utils.regex import REGEX_PROMO

from knotis.contrib.layout.views import (
    DefaultBaseView,
)

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.promocode.models import PromoCode


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

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        promo_code_id = request.POST.get('promo_code')

        promo_code = get_object_or_404(
            PromoCode,
            pk=promo_code_id
        )
        current_identity = self.get_current_identity(request)
        promo_code.execute(current_identity)

        data = {}
        errors = {}

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )
