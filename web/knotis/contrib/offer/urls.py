from django.contrib.auth.decorators import login_required

from django.conf.urls.defaults import (
    patterns,
    url
)

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
        r'/purchase/$',
        login_required(OfferPurchaseButton.as_view())
    )
)

urlpatterns += OffersView.urls()
urlpatterns += OfferDetailView.urls()
urlpatterns += OfferPurchaseView.urls(require_login=True)
urlpatterns += OfferPurchaseSuccessView.urls(require_login=True)
