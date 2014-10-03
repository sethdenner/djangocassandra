from django.conf.urls.defaults import (
    patterns,
    url
)

from django.contrib.auth.decorators import login_required

from knotis.utils.regex import REGEX_UUID

from views import (
    EstablishmentProfileView,
    EstablishmentAboutDetails,
    CreateBusinessView,
    MyEstablishmentsView,
    MyOffersView,
    MyCustomersView,
    MyAnalyticsView,
    MyRedemptionsView,
    RedemptionsGrid,
    OfferRedemptionView,
    OfferEditView,
    OfferEditProductFormView,
    OfferEditDetailsFormView,
    OfferEditLocationFormView,
    OfferEditPublishFormView,
    OfferEditSummaryView,
)

urlpatterns = patterns(
    '',
    url(
        r'^my/establishments/$',
        login_required(MyEstablishmentsView.as_view())
    ),
    url(
        r''.join([
            '^my/offers/redeem/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ]),
        login_required(OfferRedemptionView.as_view())
    ),
    url(
        r'^my/offers(/(?P<offer_filter>\w*))?/$',
        login_required(MyOffersView.as_view())
    ),
    url(
        r'^my/analytics(/(?P<graph_type>\w*))?/$',
        login_required(MyAnalyticsView.as_view())
    ),
    url(
        r'^offer/create/product/$',
        OfferEditProductFormView.as_view(),
        name=OfferEditProductFormView.view_name
    ),
    url(
        r'^offer/create/details/$',
        OfferEditDetailsFormView.as_view(),
        name=OfferEditDetailsFormView.view_name
    ),
    url(
        r'^offer/create/location/$',
        OfferEditLocationFormView.as_view(),
        name=OfferEditLocationFormView.view_name
    ),
    url(
        r'^offer/create/publish/$',
        OfferEditPublishFormView.as_view(),
        name=OfferEditPublishFormView.view_name
    ),
    url(
        r'^offer/create/summary/$',
        OfferEditSummaryView.as_view(),
        name=OfferEditSummaryView.view_name
    ),
    url(
        r'^identity/update_profile/',
        EstablishmentAboutDetails.as_view()
    ),
    url(
        r'^my/redemptions/((?P<redemption_filter>\w*)/)?grid/((?P<page>\d+)/)?((?P<count>\d+)/)?$',
        RedemptionsGrid.as_view()
    ),
)

urlpatterns += MyCustomersView.urls(require_login=True)
urlpatterns += MyRedemptionsView.urls(require_login=True)
urlpatterns += MyOffersView.urls(require_login=True)
urlpatterns += OfferEditView.urls(require_login=True)
urlpatterns += EstablishmentProfileView.urls()
urlpatterns += CreateBusinessView.urls()
