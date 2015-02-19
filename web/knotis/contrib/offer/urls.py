from django.contrib.auth.decorators import login_required

from django.conf.urls.defaults import (
    patterns,
    url
)

from .views import (
    OffersView,
    OfferDetailView,
    OfferPurchaseView,
    OffersGridView,
    PassportBookView,
    OfferPurchaseSuccessView,
    OfferPurchaseButton,
    PassportDistributionView
)

from .emails import (
    NewOfferEmailView
)

urlpatterns = patterns(
    'knotis.contrib.offer.views',
    url(
        r'^newoffer$',
        NewOfferEmailView.as_view()
    ),
    url(
        r'/purchase/$',
        login_required(OfferPurchaseButton.as_view())
    ),
    url(
        r'^/grid/(?P<page>\d+)/(?P<count>\d+)/$',
        OffersGridView.as_view()
    ),
)

urlpatterns += OfferDetailView.urls()
urlpatterns += OffersView.urls()
urlpatterns += PassportBookView.urls()
urlpatterns += OfferPurchaseView.urls(require_login=True)
urlpatterns += OfferPurchaseSuccessView.urls(require_login=True)
urlpatterns += PassportDistributionView.urls()
