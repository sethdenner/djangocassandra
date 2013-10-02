from django.conf.urls.defaults import (
    patterns
)

from api import RelationApi

urlpatterns = patterns(
    'knotis.contrib.relation.views',
    RelationApi.urls()
)
