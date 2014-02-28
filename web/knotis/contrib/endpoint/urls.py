from django.conf.urls.defaults import (
    patterns,
    url
)

from api import (
    EndpointApi
)

from views import(
    SocialMediaSettingsView,
    DeleteEndpointView
)

urlpatterns = patterns(
    '',
    EndpointApi.urls(),
    url(
        r'^settings/social/$',
        SocialMediaSettingsView.as_view()
    ),
    url(
        r'^endpoint/delete/$',
        DeleteEndpointView.as_view()
    ),
)
