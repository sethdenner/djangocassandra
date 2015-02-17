from django.conf.urls import (
    patterns,
    url

)
from django.views.generic.simple import redirect_to

from knotis.utils.regex import REGEX_UUID

from .views import (
    EstablishmentsView,
    EstablishmentsGrid,
    IdentitySwitcherView,
    FirstIdentityView,
)


urlpatterns = patterns(
    'knotis.contrib.identity.views',
    url(
        r'^businesses/grid/(?P<page>\d+)/(?P<count>\d+)/$',
        EstablishmentsGrid.as_view()
    ),
    url(
        r''.join([
            '^business/(?P<business_id>',
            REGEX_UUID,
            ')/$'
        ]),
        redirect_to,
        {'url': '/id/%(business_id)s/'}
    ),
    url(
        r''.join([
            '^identity/switcher(/(?P<identity_id>',
            REGEX_UUID,
            '))?/$'
        ]),
        IdentitySwitcherView.as_view()
    ),
    url(
        r'^identity/first/$',
        FirstIdentityView.as_view()
    ),
)

urlpatterns += EstablishmentsView.urls()
urlpatterns += IdentitySwitcherView.urls()
urlpatterns += FirstIdentityView.urls()
