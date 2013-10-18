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
    IdentityApi.urls(),
    IdentityIndividualApi.urls(),
    IdentityBusinessApi.urls(),
    IdentityEstablishmentApi.urls(),
    LocationApi.urls(),
    RedemptionApi.urls(login_required=True),
    RelationApi.urls(),
    FollowApi.urls()
)
