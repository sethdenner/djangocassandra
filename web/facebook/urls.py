from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('facebook.views',
    url(
        r'^channel/$',
        'channel',
        name='facebook'
    ),
    url(
        r'^login(/(?P<account_type>[^/]+))?/$',
        'login',
        name='facebook'
    )
)
