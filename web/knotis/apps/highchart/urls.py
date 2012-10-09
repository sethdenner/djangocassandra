from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'knotis.apps.highchart.views',
    url(
        r'revenue/daily(/(?P<business_id>[^/]+))?/$',
        'get_revenue_chart', {
            'scope': 'daily'
        }
    ),
    url(
        r'revenue/weekly(/(?P<business_id>[^/]+))?/$',
        'get_revenue_chart', {
            'scope': 'weekly'
        }
    ),
    url(
        r'revenue/monthly(/(?P<business_id>[^/]+))?/$',
        'get_revenue_chart', {
            'scope': 'monthly'
        }
    ),
    url(
        r'scans/daily(/(?P<business_id>[^/]+))?/$',
        'get_qrcode_chart', {
            'scope': 'daily'
        }
    ),
    url(
        r'scans/weekly(/(?P<business_id>[^/]+))?/$',
        'get_qrcode_chart', {
            'scope': 'weekly'
        }
    ),
    url(
        r'scans/monthly(/(?P<business_id>[^/]+))?/$',
        'get_qrcode_chart', {
            'scope': 'monthly'
        }
    )
)
