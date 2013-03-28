from django.conf.urls.defaults import (
    patterns,
    url
)

from views import IdentitySwitcherView

urlpatterns = patterns(
    'knotis.contrib.identity.views',
    url(
        r'^identity/switcher/$',
        IdentitySwitcherView.as_view()
    ),
)
