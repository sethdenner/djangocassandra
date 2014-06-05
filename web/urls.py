from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# This code is required for template fragments
# to find the corresponding views

from knotis.views import (
    RenderTemplateFragmentMixin
)
RenderTemplateFragmentMixin.register_template_fragment_views()

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        r'',
        include('knotis.core.urls')
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
        include('knotis.contrib.search.urls')
    ),
    url(
        r'',
        include('knotis.contrib.api.urls')
    ),
    url(
        r'',
        include('knotis.contrib.endpoint.urls')
    ),
    url(
        r'',
        include('knotis.contrib.legacy.urls')
    ),
    url(
        r'^facebook/',
        include('knotis.contrib.facebook.urls')
    ),
    url(
        r'^twitter/',
        include('knotis.contrib.twitter.urls')
    ),
    url(
        r'^stripe/',
        include('knotis.contrib.stripe.urls')
    ),
    url(
        r'',
        include('knotis.contrib.transaction.urls')
    ),
    url(
        r'',
        include('knotis.contrib.support.urls')
    ),
)
