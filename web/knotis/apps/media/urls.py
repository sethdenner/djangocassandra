from django.conf import settings
from django.conf.urls.defaults import (
    patterns,
    url
)


urlpatterns = patterns(
    'knotis.apps.media.views',
    url(
        r'ajax/',
        'ajax'
    ),
    url(
        r'(?P<path>.+)/$',
        'xsendfileserve', {
            'document_root': settings.MEDIA_ROOT
        },
    ),
)
