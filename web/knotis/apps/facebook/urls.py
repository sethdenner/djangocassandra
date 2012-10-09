from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'knotis.apps.facebook.views',
    url(
        r'channel/$',
        'channel'
    )
)
