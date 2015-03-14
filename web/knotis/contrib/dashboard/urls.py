from django.conf.urls import (
    patterns,
    url
)


urlpatterns = patterns(
    'knotis.contrib.dashboard.views',
    url(
        r'^[/]?$',
        'dashboard',
    ),
    url(
        r'^qrcodes/$',
        'dashboard_qrcode'
    ),
)
