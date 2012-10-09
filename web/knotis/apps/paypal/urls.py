from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('paypal.views',
    url(
        r'^ipn/$',
        'ipn_callback'
    )
)
