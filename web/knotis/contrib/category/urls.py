from django.conf.urls import (
    patterns,
    url
)


urlpatterns = patterns(
    'knotis.contrib.category.views',
    url(
        r'neighborhood/(?P<city>[^/]+)*/$',
        'get_neighborhoods',
    ),
)
