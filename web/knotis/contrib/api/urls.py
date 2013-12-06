from django.conf.urls.defaults import (
    patterns
)

from knotis.contrib.auth.api import (
    AuthUserApi,
    AuthenticationApi,
    AuthForgotPasswordApi
)
from knotis.contrib.identity.api import (
    IdentityApi,
    IdentityIndividualApi,
    IdentityBusinessApi,
    IdentityEstablishmentApi
)

from knotis.contrib.offer.api import (
    OfferApi,
    OfferPublishApi
)
from knotis.contrib.location.api import LocationApi
from knotis.contrib.merchant.api import RedemptionApi
from knotis.contrib.relation.api import (
    RelationApi,
    FollowApi
)


urlpatterns = patterns(
    '',
    AuthUserApi.urls(),
    AuthenticationApi.urls(),
    AuthForgotPasswordApi.urls(),
    IdentityApi.urls(login_required=True),
    IdentityIndividualApi.urls(login_required=True),
    IdentityBusinessApi.urls(login_required=True),
    IdentityEstablishmentApi.urls(login_required=True),
    OfferApi.urls(login_required=True),
    OfferPublishApi.urls(login_required=True),
    LocationApi.urls(login_required=True),
    RedemptionApi.urls(login_required=True),
    RelationApi.urls(),
    FollowApi.urls()
)
