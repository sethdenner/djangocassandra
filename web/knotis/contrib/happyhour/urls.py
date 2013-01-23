from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis.contrib.happyhour.views',
    url(
        r'^[/]?$',
        'index'
    ),
)
