from django.conf.urls.defaults import (
    patterns
)

from api import (
    RelationApi,
    FollowApi
)

urlpatterns = patterns(
    'knotis.contrib.relation.views',
    RelationApi.urls(),
    FollowApi.urls()
)
