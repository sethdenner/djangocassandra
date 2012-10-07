from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        r'',
        include('knotis.urls')
    ),
)

urlpatterns += staticfiles_urlpatterns()
