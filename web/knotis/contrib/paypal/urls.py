from django.conf.urls import (
    patterns,
    url
)

from views import (
    IPNCallbackView,
    PayPalReturn
)

urlpatterns = patterns(
    'knotis.contrib.paypal.views',
    url(
        r'^ipn/$',
        IPNCallbackView.as_view()
    ),
    url(
        r'^return/$',
        PayPalReturn.as_view()
    ),
)
