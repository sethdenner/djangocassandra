from django.conf.urls import patterns, url

urlpatterns = patterns(
    'knotis.contrib.event.views',
    url(
        r'^[/]?$',
        'index'
    )
)
