from django.conf.urls import patterns, url

urlpatterns = patterns(
    'knotis.contrib.contact.views',
    url(
        r'^[/]?$',
        'contact'
    ),
)
