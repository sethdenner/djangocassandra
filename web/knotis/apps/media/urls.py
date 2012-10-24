from django.conf import settings
from django.conf.urls.defaults import (
    patterns,
    url
)


urlpatterns = patterns(
    'knotis.apps.media.views',
    url(
        r'^image/ajax/',
        'ajax'
    ),
    url(
        r'^media/(?P<path>.+)/$',
        'xsendfileserve', {
            'document_root': settings.MEDIA_ROOT
        },
    ),
)
