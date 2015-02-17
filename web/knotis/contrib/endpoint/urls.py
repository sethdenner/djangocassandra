from django.conf.urls import (
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
        r'^endpoint/delete/$',
        DeleteEndpointView.as_view()
    ),
)

urlpatterns += SocialMediaSettingsView.urls()