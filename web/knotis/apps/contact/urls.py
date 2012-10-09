from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis.apps.contact.views',
    url(
        r'^[/]?$',
        'contact'
    ),
)
