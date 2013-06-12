from django.conf.urls.defaults import (
    patterns,
    url
)

from api import (
    IdentityApi,
    IdentityIndividualApi,
    IdentityBusinessApi,
    IdentityEstablishmentApi
)
from views import (
    IdentitySwitcherView,
    FirstIdentityView
)

urlpatterns = patterns(
    'knotis.contrib.identity.views',
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
