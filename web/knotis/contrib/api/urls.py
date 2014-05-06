from django.conf.urls.defaults import (
    patterns
)

from knotis.contrib.auth.api import (
    AuthUserApiView,
    AuthenticationApiView,
    AuthForgotPasswordApiView
)
from knotis.contrib.identity.api import (
    IdentityApiView,
    IdentityIndividualApiView,
    IdentityBusinessApiView,
    IdentityEstablishmentApiView
)

from knotis.contrib.offer.api import (
    OfferApiView,
    OfferPublishApiView
)
from knotis.contrib.location.api import LocationApiView
from knotis.contrib.relation.api import (
    RelationApiView,
    FollowApiView
)

from knotis.contrib.media.api import (
    ImageApiView,
    ImageInstanceApiView
)


urlpatterns = patterns(
    '',
    AuthUserApiView.urls(login_required=False),
    AuthenticationApiView.urls(login_required=False),
    AuthForgotPasswordApiView.urls(login_required=True),
    IdentityApiView.urls(),
    IdentityIndividualApiView.urls(),
    IdentityBusinessApiView.urls(),
    IdentityEstablishmentApiView.urls(),
    OfferApiView.urls(),
    OfferPublishApiView.urls(),
    LocationApiView.urls(),
    RelationApiView.urls(),
    FollowApiView.urls(),
    ImageApiView.urls(),
    ImageInstanceApiView.urls()
)
