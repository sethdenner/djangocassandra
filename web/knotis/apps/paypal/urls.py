from django.conf.urls.defaults import (
    patterns,
    url
)


urlpatterns = patterns(
    'knotis.apps.paypal.views',
    url(
        r'^ipn/$',
        'ipn_callback'
    )
)
