from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(
        r'',
        include('knotis.apps.auth.urls')
    ),
    url(
        r'',
        include('knotis.apps.core.urls')
    ),
    url(
        r'',
        include('knotis.apps.legacy.urls')
    ),
    url(
        r'',
        include('knotis.apps.business.urls')
    ),
    url(
        r'^offer',
        include('knotis.apps.offer.urls')
    ),
    url(
        r'^charts/',
        include('knotis.apps.highchart.urls')
    ),
    url(
        r'^contact/',
        include('knotis.apps.contact.urls'),
    ),
    url(
        r'^events/',
        include('knotis.apps.event.urls'),
    ),
    url(
        r'^happyhours/',
        include('knotis.apps.happyhour.urls'),
    ),
    url(
        r'^dashboard/',
        include('knotis.apps.dashboard.urls')
    ),
    url(
        r'^qrcode/',
        include('knotis.apps.qrcode.urls')
    ),
    url(
        r'^media/',
        include('knotis.apps.media.urls')
    ),
    url(
        r'^category/',
        include('knotis.apps.category.urls')
    ),
    url(
        r'^paypal/',
        include('knotis.apps.paypal.urls')
    ),
    url(
        r'^admin/doc/',
        include('django.contrib.admindocs.urls')
    ),
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^api/',
        include('knotis.apps.api.urls')
    ),
    url(
        r'^(?P<backend_name>[^/]+)/$',
        'knotis.apps.business.views.profile',
    ),
)


urlpatterns += staticfiles_urlpatterns()
