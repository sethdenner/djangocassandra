from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

from views import (
    MyEstablishmentsView,
    MyOffersView,
    MyFollowersView,
    MyAnalyticsView,
    OfferRedemptionView
)

urlpatterns = patterns(
    '',
    url(
        r'^establishments/$',
        MyEstablishmentsView.as_view()
    ),
    url(
        r''.join([
            '^offers/redeem/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ]),
        OfferRedemptionView.as_view()
    ),
    url(
        r'^offers(/(?P<offer_filter>\w*))?/$',
        MyOffersView.as_view()
    ),
    url(
        r'^followers/$',
        MyFollowersView.as_view()
    ),
    url(
        r'^analytics(/(?P<graph_type>\w*))?/$',
        MyAnalyticsView.as_view()
    )
)
