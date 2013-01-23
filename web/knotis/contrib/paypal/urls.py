from django.conf.urls.defaults import (
    patterns,
    url
)


urlpatterns = patterns(
    'knotis.contrib.paypal.views',
    url(
        r'^ipn/$',
        'ipn_callback'
    ),
    url(
        r'^return/$',
        'paypal_return'
    ),
)
