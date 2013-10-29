from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# This code is required for template fragments
# to find the corresponding views

from knotis.views.mixins import RenderTemplateFragmentMixin
RenderTemplateFragmentMixin.register_template_fragment_views()


admin.autodiscover()

from knotis.contrib.identity.views import BusinessesView

urlpatterns = patterns(
    '',
    url(
        r'^[/]?$',
        BusinessesView.as_view()
    ),
    url(
        r'',
        include('knotis.contrib.identity.urls')
    ),
    url(
        r'',
        include('knotis.contrib.relation.urls')
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
        r'^my/',
        include('knotis.contrib.merchant.urls')
    ),
    url(
        r'^my/',
        include('knotis.contrib.consumer.urls')
    ),
    url(
        r'^offer',
        include('knotis.contrib.offer.urls')
    ),
    url(
        r'',
        include('knotis.contrib.qrcode.urls')
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
        r'',
        include('knotis.contrib.location.urls')
    ),
    url(
        r'',
        include('knotis.contrib.api.urls')
    ),
    url(
        r'',
        include('knotis.contrib.endpoint.urls')
    )
)
