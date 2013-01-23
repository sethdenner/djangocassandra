from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis.contrib.contact.views',
    url(
        r'^[/]?$',
        'contact'
    ),
)
