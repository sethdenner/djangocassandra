from django.conf.urls.defaults import (
    url, 
    patterns
)

from knotis.utils.regex import REGEX_UUID

urlpatterns = patterns(
    'knotis.apps.transaction.views',
    url(
        r''.join([
            '^offer/print/(?P<transaction_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'print_transaction'
    ),
    url(
        r'^offers/get_user_offers/(?P<status>[\D]+)/$',
        'get_user_transactions'
    ),
)
