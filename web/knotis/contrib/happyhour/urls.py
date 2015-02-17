from django.conf.urls import patterns, url

urlpatterns = patterns(
    'knotis.contrib.happyhour.views',
    url(
        r'^[/]?$',
        'index'
    ),
)
