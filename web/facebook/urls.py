from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'facebook.views',
    url(
        r'^channel/$',
        'channel'
    ),
)
