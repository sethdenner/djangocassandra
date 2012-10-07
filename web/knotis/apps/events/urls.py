from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis_events.views',
    url(
        r'^/',
        'index'
    )
)