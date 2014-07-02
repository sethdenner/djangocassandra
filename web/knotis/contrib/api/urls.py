from django.conf.urls.defaults import (
    patterns
)

from knotis.contrib.auth.api import (
    AuthUserApiView,
    AuthenticationApiView,
    AuthForgotPasswordApiView,
    UserInformationApiModelViewSet
)
from knotis.contrib.identity.api import (
    IdentityApiView,
    IdentityIndividualApiView,
    IdentityBusinessApiView,
    IdentityEstablishmentApiView,
    IdentityApiModelViewSet,
    IdentitySwitcherApiViewSet,
    IndividualApiModelViewSet,
    EstablishmentApiModelViewSet,
    BusinessApiModelViewSet
)

from knotis.contrib.offer.api import (
    OfferApiView,
    OfferPublishApiView,
    OfferApiModelViewSet,
    OfferAvailabilityModelViewSet
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

from knotis.contrib.transaction.api import (
    PurchaseApiModelViewSet,
    RedemptionApiModelViewSet
)

from knotis.contrib.stripe.api import (
    StripeCustomerModelViewSet
)

from knotis.contrib.qrcode.api import RedemptionScanApiViewSet

urlpatterns = patterns('')
urlpatterns += AuthUserApiView.urls()
urlpatterns += AuthenticationApiView.urls()
urlpatterns += AuthForgotPasswordApiView.urls()
urlpatterns += UserInformationApiModelViewSet.urls()
urlpatterns += IndividualApiModelViewSet.urls()
urlpatterns += EstablishmentApiModelViewSet.urls()
urlpatterns += BusinessApiModelViewSet.urls()
urlpatterns += IdentityApiView.urls()
urlpatterns += IdentityIndividualApiView.urls()
urlpatterns += IdentityBusinessApiView.urls()
urlpatterns += IdentityEstablishmentApiView.urls()
urlpatterns += IdentitySwitcherApiViewSet.urls()
urlpatterns += IdentityApiModelViewSet.urls()
urlpatterns += OfferApiModelViewSet.urls()
urlpatterns += OfferApiView.urls()
urlpatterns += OfferPublishApiView.urls()
urlpatterns += OfferAvailabilityModelViewSet.urls()
urlpatterns += LocationApiView.urls()
urlpatterns += RelationApiView.urls()
urlpatterns += FollowApiView.urls()
urlpatterns += ImageApiView.urls()
urlpatterns += ImageInstanceApiView.urls()
urlpatterns += SearchApiViewSet.urls()
urlpatterns += EndpointApi.urls()
urlpatterns += PurchaseApiModelViewSet.urls()
urlpatterns += RedemptionApiModelViewSet.urls()
urlpatterns += StripeCustomerModelViewSet.urls()
urlpatterns += RedemptionScanApiViewSet.urls()
