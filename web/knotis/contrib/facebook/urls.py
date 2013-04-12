from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'knotis.contrib.facebook.views',
    url(
        r'channel/$',
        'channel'
    )
)
