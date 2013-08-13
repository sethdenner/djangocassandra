from django.conf.urls.defaults import (
    patterns,
    url
)

from views import (
    OfferEditView,
    OfferEditProductFormView,
    OfferEditDetailsFormView,
    OfferEditLocationFormView,
    OfferEditPublishFormView,
    OfferEditSummaryView
)

urlpatterns = patterns(
    'knotis.contrib.offer.views',
    url(
        r'/create/$',
        OfferEditView.as_view()
    ),
    url(
        r'/create/product/$',
        OfferEditProductFormView.as_view()
    ),
    url(
        r'/create/details/$',
        OfferEditDetailsFormView.as_view()
    ),
    url(
        r'/create/location/$',
        OfferEditLocationFormView.as_view()
    ),
    url(
        r'/create/publish/$',
        OfferEditPublishFormView.as_view()
    ),
    url(
        r'/create/summary/$',
        OfferEditSummaryView.as_view()
    )
)
