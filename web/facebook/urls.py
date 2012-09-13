from django.conf.urls.defaults import patterns


urlpatterns = patterns('facebook.views',
    (r'^channel/$', 'channel'),
)
