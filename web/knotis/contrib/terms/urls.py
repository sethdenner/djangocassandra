
from django.conf.urls.defaults import patterns, url

from views import (
    TermsAndConditionsView,
    PrivacyView
)

urlpatterns = patterns(
    '',
    url(
        r'^terms-and-conditions/$',
        TermsAndConditionsView.as_view()
    ),
    url(
        r'^privacy/$',
        PrivacyView.as_view()
    ),
)
