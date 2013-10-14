from django.conf.urls.defaults import (
    patterns,
    url

)
from django.views.generic.simple import redirect_to

from knotis.utils.regex import REGEX_UUID

from views import (
    IdentityView,
    BusinessesView,
    EstablishmentProfileView,
    IdentitySwitcherView,
    FirstIdentityView
)

urlpatterns = patterns(
    'knotis.contrib.identity.views',
    url(
        r''.join([
            '^id/(?P<id>',
            REGEX_UUID,
            ')(/offer/(?P<offer_id>',
            REGEX_UUID,
            '))?/$'
        ]),
        IdentityView.as_view()
    ),
    url(
        r''.join([
            '^id/(?P<id>',
            REGEX_UUID,
            ')/offers/$'
        ]),
        IdentityView.as_view()
    ),
    url(
        r'^businesses/$',
        BusinessesView.as_view()
    ),
    url(
        r''.join([
            '^business/(?P<business_id>',
            REGEX_UUID,
            ')/$'
        ]),
        redirect_to,
        {'url': '/id/%(business_id)s/'}
    ),
    url(
        r''.join([
            '^merchants/(?P<establishment_id>',
            REGEX_UUID,
            ')/$'
        ]),
        EstablishmentProfileView.as_view()
    ),
    url(
        r'^merchants/(?P<backend_name>[^/]+)/$',
        EstablishmentProfileView.as_view()
    ),
    url(
        r''.join([
            '^identity/switcher(/(?P<identity_id>',
            REGEX_UUID,
            '))?/$'
        ]),
        IdentitySwitcherView.as_view()
    ),
    url(
        r'^identity/first/$',
        FirstIdentityView.as_view()
    ),
    IdentityApi.urls(),
    IdentityIndividualApi.urls(),
    IdentityBusinessApi.urls(),
    IdentityEstablishmentApi.urls(),
    )
)
