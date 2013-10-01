from django.conf.urls.defaults import (
    patterns,
    url
)

from views import (
    MyEstablishmentsView,
    MyOffersView,
    OfferRedemptionView,
    MyFollowersView,
    MyAnalyticsView,
)

urlpatterns = patterns(
    '',
    url(
        r'^establishments/$',
        MyEstablishmentsView.as_view()
    ),
    url(
        r'^offers/redeem/',
        OfferRedemptionView.as_view()
    ),
    url(
        r'^offers(/(?P<filter>\w*))?/$',
        MyOffersView.as_view()
    ),
    url(
        r'^followers/$',
        MyFollowersView.as_view()
    ),
    url(
        r'^analytics(/(?P<graph_type>\w*))/$',
        MyAnalyticsView.as_view()
    )
)
