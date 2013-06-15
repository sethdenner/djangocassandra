from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

from api import (
    IdentityApi,
    IdentityIndividualApi,
    IdentityBusinessApi,
    IdentityEstablishmentApi
)
from views import (
    EstablishmentProfileView,
    IdentitySwitcherView,
    FirstIdentityView
)

urlpatterns = patterns(
    'knotis.contrib.identity.views',
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
        r'^identity/switcher/$',
        IdentitySwitcherView.as_view()
    ),
    url(
        r'^identity/first/$',
        FirstIdentityView.as_view()
    ),
    IdentityApi.urls(),
    IdentityIndividualApi.urls(),
    IdentityBusinessApi.urls(),
    IdentityEstablishmentApi.urls()
)
