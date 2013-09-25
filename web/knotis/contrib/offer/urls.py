from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

from views import (
    OfferDetailView,
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
        r''.join([
            '/(?P<offer_id>',
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
