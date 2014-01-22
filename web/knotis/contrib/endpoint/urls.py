from django.conf.urls.defaults import (
    patterns,
    url
)

from api import (
    EndpointApi
)

from views import(
    SocialMediaSettingsView
)

urlpatterns = patterns(
    '',
    EndpointApi.urls(),
    url(
        r'^settings/social/$',
        SocialMediaSettingsView.as_view()
    )
)
