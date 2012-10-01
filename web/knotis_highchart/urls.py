from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'knotis_highchart.views',
    url(
        r'^revenue/daily(/(?P<business_id>[^/]+))?/$',
        'get_revenue_chart', {
            'scope': 'daily'
        }
    ),
    url(
        r'^revenue/weekly(/(?P<business_id>[^/]+))?/$',
        'get_revenue_chart', {
            'scope': 'weekly'
        }
    ),
    url(
        r'^revenue/monthly(/(?P<business_id>[^/]+))?/$',
        'get_revenue_chart', {
            'scope': 'monthly'
        }
    )
)
