from django.conf.urls.defaults import (
    patterns,
    url
)

from views import OfferCreateView

urlpatterns = patterns(
    'knotis.contrib.offer.views',
    url(
        r'/create/$',
        OfferCreateView.as_view()
    ),
)
