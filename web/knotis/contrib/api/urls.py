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
from knotis.contrib.relation.api import (
    RelationApi,
    FollowApi
)

from knotis.contrib.media.api import (
    ImageApiView,
    ImageInstanceApiView
)


urlpatterns = patterns(
    '',
    AuthUserApi.urls(login_required=False),
    AuthenticationApi.urls(login_required=False),
    AuthForgotPasswordApi.urls(login_required=True),
    IdentityApi.urls(),
    IdentityIndividualApi.urls(),
    IdentityBusinessApi.urls(),
    IdentityEstablishmentApi.urls(),
    OfferApi.urls(),
    OfferPublishApi.urls(),
    LocationApi.urls(),
    RelationApi.urls(),
    FollowApi.urls(),
    ImageApiView.urls(),
    ImageInstanceApiView.urls()
)
