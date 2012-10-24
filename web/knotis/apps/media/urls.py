from django.conf import settings
from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

urlpatterns = patterns(
    'knotis.apps.media.views',
    url(
        r'^image/ajax/',
        'ajax'
    ),
    url(
        r''.join([
            '^image/get_list/(?P<related_object_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'get_image_list'
    ),
    url(
        r''.join([
            '^image/get_row/(?P<image_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'get_image_row'
    ),
    url(
        r'^media/(?P<path>.+)/$',
        'xsendfileserve', {
            'document_root': settings.MEDIA_ROOT
        },
    ),
)
