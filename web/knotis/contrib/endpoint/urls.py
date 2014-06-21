from django.conf.urls.defaults import (
    patterns,
    url
)

from views import(
    SocialMediaSettingsView,
    DeleteEndpointView
)

urlpatterns = patterns(
    '',
    url(
        r'^settings/social/$',
        SocialMediaSettingsView.as_view()
    ),
    url(
        r'^endpoint/delete/$',
        DeleteEndpointView.as_view()
    ),
)
