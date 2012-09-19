from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('paypal.views',
    url(
        r'^plan/premium/buy/$',
        'buy_premium_plan', {
            'method': 'buy_premium_plan',
            'item': 'plan_premium'
        },
        name='paypal'
    )
)
