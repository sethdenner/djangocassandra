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
        r''.join([
            '^transaction/customerreceipt/(?P<transaction_id>',
            REGEX_UUID,
            ')/$'
        ]),
        CustomerReceiptBody.as_view()
    ),
)
