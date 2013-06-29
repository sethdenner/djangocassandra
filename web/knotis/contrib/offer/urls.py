from django.conf.urls.defaults import (
    patterns,
    url
)

from views import OfferCreateView

urlpatterns = patterns(
    'knotis.contrib.offer.views',
    url(
        r'/create/(?P<form_type>.{1,16})/$',
        OfferCreateView.as_view()
    ),
)
