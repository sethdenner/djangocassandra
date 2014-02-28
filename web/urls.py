from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# This code is required for template fragments
# to find the corresponding views

from knotis.views import (
    RenderTemplateFragmentMixin
)
RenderTemplateFragmentMixin.register_template_fragment_views()

admin.autodiscover()

from knotis.contrib.offer.views import (
    NewOfferEmailBody
)

from knotis.contrib.transaction.views import (
    CustomerReceiptBody,
    MerchantReceiptBody
)

urlpatterns = patterns(
    '',
    url(
        r'^transaction/customerreceipt/$',
        CustomerReceiptBody.as_view()
    ),
    url(
        r'^transaction/merchantreceipt/$',
        MerchantReceiptBody.as_view()
    ),
    url(
        r'^newoffer$',
        NewOfferEmailBody.as_view()
    ),
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
        r'^facebook/',
        include('knotis.contrib.facebook.urls')
    ),
    url(
        r'^twitter/',
        include('knotis.contrib.twitter.urls')
    )
)
