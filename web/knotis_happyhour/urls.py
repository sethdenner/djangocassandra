from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis_happyhour.views',
    url(
        r'^/',
        'index'
    ),
)
