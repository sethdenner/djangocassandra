from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# This code is required for template fragments
# to find the corresponding views

from knotis.views.mixins import RenderTemplateFragmentMixin
RenderTemplateFragmentMixin.register_template_fragment_views()


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        r'',
        include('knotis.contrib.identity.urls')
    ),
    url(
        r'',
        include('knotis.contrib.media.urls')
    ),
    url(
        r'',
        include('knotis.contrib.auth.urls')
    ),
    url(
        r'',
        include('knotis.contrib.core.urls')
    ),
    url(
        r'',
        include('knotis.contrib.legacy.urls')
    ),
    url(
        r'',
        include('knotis.contrib.business.urls')
    ),
    url(
        r'',
        include('knotis.contrib.transaction.urls')
    ),
    url(
        r'^offer',
        include('knotis.contrib.offer.urls')
    ),
    url(
        r'^charts/',
        include('knotis.contrib.highchart.urls')
    ),
    url(
        r'^contact/',
        include('knotis.contrib.contact.urls'),
    ),
    url(
        r'^events/',
        include('knotis.contrib.event.urls'),
    ),
    url(
        r'^happyhours/',
        include('knotis.contrib.happyhour.urls'),
    ),
    url(
        r'^dashboard/',
        include('knotis.contrib.dashboard.urls')
    ),
    url(
        r'^qrcode/',
        include('knotis.contrib.qrcode.urls')
    ),
    url(
        r'^category/',
        include('knotis.contrib.category.urls')
    ),
    url(
        r'^paypal/',
        include('knotis.contrib.paypal.urls')
    ),
    url(
        r'',
        include('knotis.contrib.sickle.urls')
    ),
    url(
        r'^(?P<backend_name>[^/]+)/$',
        'knotis.contrib.business.views.profile',
    ),
    url(
        r'',
        include('knotis.contrib.layout.urls')
    )
)
