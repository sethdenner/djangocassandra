from django.contrib.auth.decorators import login_required

from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

from views import (
    OffersView,
    OfferDetailView,
    OfferEditView,
    OfferEditProductFormView,
    OfferEditDetailsFormView,
    OfferEditLocationFormView,
    OfferEditPublishFormView,
    OfferEditSummaryView,
    OfferPurchaseView,
    OfferPurchaseSuccessView,
    OfferPurchaseButton,
    NewOfferEmailBody
)



urlpatterns = patterns(
    'knotis.contrib.offer.views',
    url(
        r'^newoffer$',
        NewOfferEmailBody.as_view()
    ),
    url(
        r''.join([
            '/(?P<offer_id>',
            REGEX_UUID,
            ')/buy/$'
        ]),
        OfferPurchaseView.as_view()
    ),
    url(
        r''.join([
            '/(?P<offer_id>',
            REGEX_UUID,
            ')/buy/success/$'
        ]),
        OfferPurchaseSuccessView.as_view()
    ),
    url(
        r''.join([
            'detail/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ]),
        OfferDetailView.as_view()
    ),
    url(
        r'/create/$',
        OfferEditView.as_view()
    ),
    url(
        r'/create/product/$',
        OfferEditProductFormView.as_view(),
        name=OfferEditProductFormView.view_name
    ),
    url(
        r'/create/details/$',
        OfferEditDetailsFormView.as_view(),
        name=OfferEditDetailsFormView.view_name
    ),
    url(
        r'/create/location/$',
        OfferEditLocationFormView.as_view(),
        name=OfferEditLocationFormView.view_name
    ),
    url(
        r'/create/publish/$',
        OfferEditPublishFormView.as_view(),
        name=OfferEditPublishFormView.view_name
    ),
    url(
        r'/create/summary/$',
        OfferEditSummaryView.as_view(),
        name=OfferEditSummaryView.view_name
    ),
    url(
        r'/purchase/$',
        login_required(OfferPurchaseButton.as_view())
    )
)

urlpatterns += OffersView.urls()
