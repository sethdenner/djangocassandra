from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis.apps.happyhour.views',
    url(
        r'^[/]?$',
        'index'
    ),
)
