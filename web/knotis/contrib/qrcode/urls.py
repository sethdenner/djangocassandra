from django.conf.urls.defaults import (
    patterns,
    url
)
from django.contrib.auth.decorators import login_required

from knotis.utils.regex import REGEX_UUID

from views import (
    ScanView,
    ManageQRCodeView
)

urlpatterns = patterns(
    'knotis.contrib.qrcode.views',
    url(
        r''.join([
            '^qrcode/(?P<qrcode_id>',
            REGEX_UUID,
            ')/$'
        ]),
        ScanView.as_view(),
    ),
)

urlpatterns += ManageQRCodeView.urls()
