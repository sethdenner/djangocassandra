from django.conf.urls import patterns, url


urlpatterns = patterns(
    'knotis.contrib.legacy.views',
    url(
        r'^business/(?P<legacy_qrcode_id>[\d]+)/$',
        'qrcode_redirect'
    )
)