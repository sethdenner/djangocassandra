from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

urlpatterns = patterns(
    'knotis.apps.qrcode.views',
    url(
        r''.join([
            '^(?P<qrcode_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'scan',
    ),
    url(
        r'^manage/$',
        'manage',
    ),
)
