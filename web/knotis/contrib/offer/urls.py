from django.contrib.auth.decorators import login_required

from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

from views import (
    OffersView,
    OfferDetailView,
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
        r'/purchase/$',
        login_required(OfferPurchaseButton.as_view())
    )
)

urlpatterns += OffersView.urls()
urlpatterns += OfferDetailView.urls()
