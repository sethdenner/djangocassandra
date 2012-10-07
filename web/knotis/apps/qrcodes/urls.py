from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'knotis_qrcodes.views',
    url(
        r'^/qrcode/$',
        'qrcode'
    ),
    url(
        r'^/scan/(?P<qrcode_id>[^/]+)/$',
        'scan'
    )
)
