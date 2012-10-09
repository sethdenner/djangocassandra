from django.conf.urls.defaults import (
    patterns,
    url
)


urlpatterns = patterns(
    'knotis.apps.core.views',
    url(
        r'^(?P<login>login)?[/]?$',
        'index',
    ),
    url(
        r'^about/$',
        'about',
    ),
    url(
        r'^howitworks/$',
        'how_it_works',
    ),
    url(
        r'^story/$',
        'story',
    ),
    url(
        r'^support/$',
        'support',
    ),
    url(
        r'^terms/$',
        'terms',
    ),
    url(
        r'^privacy/$',
        'privacy',
    ),
    url(
        r'^inquire/$',
        'inquire',
    ),
)
