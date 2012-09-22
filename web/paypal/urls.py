from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('paypal.views',
    url(
        r'^service/premium/buy/$',
        'buy_premium_service',
        name='paypal'
    )
)
