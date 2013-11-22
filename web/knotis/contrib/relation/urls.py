from django.conf.urls.defaults import (
    patterns,
    url
)

from views import (
    NewPermissionEmailBody,
    NewFollowerEmailBody
)


urlpatterns = patterns(
    'knotis.contrib.relation.views',
)
