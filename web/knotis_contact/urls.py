from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'knotis_contact.views',
    url(
        r'^/$',
        'contact'
    ),
)
