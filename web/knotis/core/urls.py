from django.conf.urls.defaults import patterns, url

from views import (
    IndexView,
    TermsAndConditionsView,
    PrivacyView
)

urlpatterns = patterns(
    '',
    url(
        r'^[/]?$',
        IndexView.as_view()
    ),
    url(
        r'^terms-and-conditions/$',
        TermsAndConditionsView.as_view()
    ),
    url(
        r'^privacy/$',
        PrivacyView.as_view()
    ),
)
