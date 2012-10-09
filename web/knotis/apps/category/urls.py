from django.conf.urls.defaults import (
    patterns,
    url
)


urlpatterns = patterns(
    'knotis.apps.category.views',
    url(
        r'neighborhood/(?P<city>[^/]+)*/$',
        'get_neighborhoods',
    ),
)
