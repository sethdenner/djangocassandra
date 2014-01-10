from django.conf.urls.defaults import patterns, url

from views import (
    IndexView,
    TermsAndConditionsView
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
)
