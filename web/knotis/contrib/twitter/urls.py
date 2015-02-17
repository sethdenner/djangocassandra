from django.conf.urls import patterns, url

from views import (
    TwitterGetAuthorizeUrl,
    TwitterVerifyPINView
)

urlpatterns = patterns(
    'knotis.contrib.twitter.views',
    url(
        r'authorize/$',
        TwitterGetAuthorizeUrl.as_view()
    ),
    url(
        r'verify-pin/$',
        TwitterVerifyPINView.as_view()
    )
)
