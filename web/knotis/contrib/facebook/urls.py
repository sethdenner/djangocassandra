from django.conf.urls.defaults import patterns, url

from views import (
    FacebookAccountChoiceFragment,
    FacebookRevokeAccessView
)

urlpatterns = patterns(
    'knotis.contrib.facebook.views',
    url(
        r'choose-account/$',
        FacebookAccountChoiceFragment.as_view()
    ),
    url(
        r'revoke-access/$',
        FacebookRevokeAccessView.as_view()
    ),
    url(
        r'channel/$',
        'channel'
    )
)
