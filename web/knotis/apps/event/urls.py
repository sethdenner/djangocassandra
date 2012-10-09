from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis.apps.event.views',
    url(
        r'^[/]?$',
        'index'
    )
)
