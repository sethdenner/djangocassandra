from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis.contrib.event.views',
    url(
        r'^[/]?$',
        'index'
    )
)
