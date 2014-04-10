from django.contrib.auth.decorators import login_required

from django.conf.urls.defaults import (
    patterns,
    url
)
from django.views.generic.simple import redirect_to

from knotis.utils.regex import REGEX_UUID

from views import (
    MyPurchasesView,
    MyRelationsView,
    PrintedVoucher,
    DownloadPrintedVoucher
)

urlpatterns = patterns(
    '',
    url(
        '^purchases(/(?P<purchase_filter>\w*))?/$',
        login_required(MyPurchasesView.as_view())
    ),
    url(
        '^following/$',
        redirect_to,
        {'url': '../relations/'}
    ),
    url(
        '^relations/following(/(?P<filter>)\w*)?/$',
        MyRelationsView
    ),
    url(
        '^relations(/(?P<filter>)\w*)?/$',
        MyRelationsView
    ),
    url(
        r''.join([
            '^purchases/',
            '(?P<transaction_id>',
            REGEX_UUID,
            ')/printable/$'
        ]),
        login_required(PrintedVoucher.as_view())
    ),
    url(
        r''.join([
            '^purchases/',
            '(?P<transaction_id>',
            REGEX_UUID,
            ')/printable/download/$'
        ]),
        login_required(DownloadPrintedVoucher.as_view())
    )
)
