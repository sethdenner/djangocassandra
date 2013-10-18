from django.conf.urls.defaults import (
    patterns
)

from knotis.contrib.auth.api import (
    AuthUserApi,
    AuthenticationApi
)
from knotis.contrib.identity.api import (
    IdentityApi,
    IdentityIndividualApi,
    IdentityBusinessApi,
    IdentityEstablishmentApi
)

from knotis.contrib.offer.api import OfferApi
from knotis.contrib.location.api import LocationApi
from knotis.contrib.merchant.api import RedemptionApi


urlpatterns = patterns(
    '',
    AuthUserApi.urls(),
    AuthenticationApi.urls(),
    IdentityApi.urls(),
    IdentityIndividualApi.urls(),
    IdentityBusinessApi.urls(),
    IdentityEstablishmentApi.urls(),
    OfferApi.urls(),
    LocationApi.urls(),
    RedemptionApi.urls(login_required=True)
)
