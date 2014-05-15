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
    OfferPublishApiView,
    OfferApiModelViewSet
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

from knotis.contrib.endpoint.api import (
    EndpointApi
)

from knotis.contrib.search.api import (
    SearchApiViewSet
)

urlpatterns = patterns('')
urlpatterns += AuthUserApiView.urls()
urlpatterns += AuthenticationApiView.urls()
urlpatterns += AuthForgotPasswordApiView.urls()
urlpatterns += IdentityApiView.urls()
urlpatterns += IdentityIndividualApiView.urls()
urlpatterns += IdentityBusinessApiView.urls()
urlpatterns += IdentityEstablishmentApiView.urls()
urlpatterns += OfferApiView.urls()
urlpatterns += OfferPublishApiView.urls()
urlpatterns += OfferApiModelViewSet.urls()
urlpatterns += LocationApiView.urls()
urlpatterns += RelationApiView.urls()
urlpatterns += FollowApiView.urls()
urlpatterns += ImageApiView.urls()
urlpatterns += ImageInstanceApiView.urls()
urlpatterns += SearchApiViewSet.urls()
urlpatterns += EndpointApi.urls()
