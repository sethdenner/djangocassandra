from django.conf.urls.defaults import (
    patterns,
    url
)

from api import (
    EndpointApi
)

urlpatterns = patterns(
    '',
    EndpointApi.urls()
)
