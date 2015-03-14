from django.conf import settings
from django.conf.urls import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

from views import ImageUploadView

urlpatterns = patterns(
    'knotis.contrib.media.views',
    url(
        r'image/upload/',
        ImageUploadView.as_view()
    ),
    url(
        r'^image/ajax/',
        'ajax'
    ),
    url(
        r''.join([
            '^image/delete/(?P<image_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'delete_image'
    ),
    url(
        r'^media/(?P<path>.+)$',
        'xsendfileserve', {
            'document_root': settings.MEDIA_ROOT
        },
    ),
)
