from django.conf.urls.defaults import (
    patterns,
    url

)
from django.views.generic.simple import redirect_to

from knotis.utils.regex import REGEX_UUID

from views import (
    IdentityView,
    BusinessesView,
    BusinessesGrid,
    EstablishmentProfileView,
    IdentitySwitcherView,
    FirstIdentityView,
    EstablishmentAboutAbout,
)


urlpatterns = patterns(
    'knotis.contrib.identity.views',
    url(
        r'^identity/update_profile/',
        EstablishmentAboutAbout.as_view()
    ),
    url(
        r''.join([
            '^id/(?P<id>',
            REGEX_UUID,
            ')(/(?P<view_name>',
            '\w{1,50}',
            '))?/$'
        ]),
        IdentityView.as_view()
    ),
    url(
        r''.join([
            '^id/(?P<id>',
            REGEX_UUID,
            ')(/offer/(?P<offer_id>',
            REGEX_UUID,
            '))?/$'
        ]),
        IdentityView.as_view()
    ),
    url(
        r''.join([
            '^id/(?P<id>',
            REGEX_UUID,
            ')/offers/$'
        ]),
        IdentityView.as_view()
    ),
    url(
        r'^businesses/$',
        BusinessesView.as_view()
    ),
    url(
        r'^businesses/grid/(?P<page>\d+)/(?P<count>\d+)/$',
        BusinessesGrid.as_view()
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
            '^merchants/(?P<establishment_id>',
            REGEX_UUID,
            ')/$'
        ]),
        EstablishmentProfileView.as_view()
    ),
    url(
        r'^merchants/(?P<backend_name>[^/]+)/$',
        EstablishmentProfileView.as_view()
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
    )
)
