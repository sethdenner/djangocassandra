from django.conf.urls.defaults import (
    patterns,
    url
)

from django.contrib.auth.decorators import login_required

from knotis.utils.regex import REGEX_UUID

from views import (
    MyEstablishmentsView,
    MyOffersView,
    MyCustomersView,
    MyFollowersView,
    MyAnalyticsView,
    OfferRedemptionView
)

urlpatterns = patterns(
    '',
    url(
        r'^establishments/$',
        login_required(MyEstablishmentsView.as_view())
    ),
    url(
        r''.join([
            '^offers/redeem/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ]),
        login_required(OfferRedemptionView.as_view())
    ),
    url(
        r'^offers(/(?P<offer_filter>\w*))?/$',
        login_required(MyOffersView.as_view())
    ),
    url(
        r'^followers/$',
        login_required(MyFollowersView.as_view())
    ),
    url(
        r'^customers/$',
        login_required(MyCustomersView.as_view())
    ),
    url(
        r'^analytics(/(?P<graph_type>\w*))?/$',
        login_required(MyAnalyticsView.as_view())
    )
)
