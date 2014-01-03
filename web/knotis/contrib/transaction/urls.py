from django.conf.urls.defaults import (
    url,
    patterns
)

from knotis.utils.regex import REGEX_UUID

from views import MerchantReceiptBody, CustomerReceiptBody

urlpatterns = patterns(
    'knotis.contrib.transaction.views',

    url(
        r'^transaction/merchantreceipt/$',
        MerchantReceiptBody.as_view()
    ),
    url(
        r'^transaction/customerreceipt/$',
        CustomerReceiptBody.as_view()
    ),
    
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
