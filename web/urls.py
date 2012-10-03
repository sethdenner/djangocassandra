from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from app.models.offers import OfferSort

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


REGEX_BACKEND_NAME = (
    '[a-zA-Z]+[a-zA-Z0-9-_]*'
)


REGEX_UUID = (
    '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
)


REGEX_CATEGORY = (
    'tra|sho|res|rea|pub|pro|'
    'pet|nig|leg|hom|hea|foo|'
    'fin|edu|bea|aut|art|all'
)


REGEX_NOT_CATEGORY_PREVIOUS = ''.join([
    '(?<!',
    REGEX_CATEGORY,
    ')'
])


REGEX_OFFER_FILTERING = ''.join([
    '(/(?P<business>',
    REGEX_BACKEND_NAME,
    REGEX_NOT_CATEGORY_PREVIOUS,
    '(?<!premium)))?(/(?P<category>',
    REGEX_CATEGORY,
    '))?(/(?P<premium>premium))?',
    '(/(?P<page>[\d]+))?',
])


urlpatterns = patterns('',
    url(
        r'',
        include('legacy.urls')
    ),

    url(
        r'^facebook/',
        include('facebook.urls')
    ),
    url(
        r'^charts/',
        include('knotis_highchart.urls')
    ),
    url(
        r'^(?P<login>login)?(/)*$',
        'app.views.home.index',
    ),
    url(
        r'^plans/$',
        'app.views.home.plans',
    ),
    url(
        r'^contact',
        include('knotis_contact.urls'),
    ),
    url(
        r'^about/$',
        'app.views.home.about',
    ),
    url(
        r'^howitworks/$',
        'app.views.home.how_it_works',
    ),
    url(
        r'^story/$',
        'app.views.home.story',
    ),
    url(
        r'^inquire/$',
        'app.views.home.inquire',
    ),
    url(
        r'^support/$',
        'app.views.home.support',
    ),
    url(
        r'^terms/$',
        'app.views.home.terms',
    ),
    url(
        r'^privacy/$',
        'app.views.home.privacy',
    ),
    url(
        r'^events',
        include('knotis_events.urls'),
    ),
    url(
        r'^happyhours',
        include('knotis_happyhour.urls'),
    ),
    url(
        r'^dashboard/$',
        'app.views.dashboard.dashboard',
    ),
    url(
        r'^dashboard/qrcodes/$',
        'app.views.dashboard.dashboard_qrcode'
    ),
    url(
        r''.join([
            '^offer/delete/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'app.views.offer.delete_offer'
    ),
    url(
        r'^offer/(?P<offer_id>[^/]+)/$',
        'app.views.offer.offer',
    ),
    url(
        r'^offers/dashboard/$',
        'app.views.offer.dashboard',
    ),
    url(
        '^offers/print_unredeemed',
        'app.views.offer.print_unredeemed',
    ),
    url(
        r'^offers/get_offers_by_status/(?P<status>[a-zA-Z_-]+)/$',
        'app.views.offer.get_offers_by_status',
    ),
    url(
        r''.join([
            '^offers/get_popular_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.get_available_offers',
        {'sort_by': OfferSort.POPULAR},
    ),
    url(
        r''.join([
            '^offers/get_newest_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.get_available_offers',
        {'sort_by': OfferSort.NEWEST},
    ),
    url(
        r''.join([
            '^offers/get_expiring_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.get_available_offers',
        {'sort_by': OfferSort.EXPIRING},
    ),
    url(
        r'^offers/update/$',
        'app.views.offer.update',
    ),
    url(
        r''.join([
            '^offers/offer_map',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.offer_map',
    ),
    url(
        r''.join([
            '^offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.offers',
    ),
    url(
        r'^business/offers/create/$',
        'app.views.offer.edit',
    ),
    url(
        r'^profile/$',
        'app.views.user.profile',
    ),
    url(
        r'^profile/update/$',
        'app.views.user.profile_ajax',
    ),
    url(
        r'^business/offers/update/(?P<offer_id>[^/]+)/$',
        'app.views.offer.edit',
    ),
    url(
        r'^business/follow/$',
        'app.views.business.follow',
        {'subscribe': True},
    ),
    url(
        r'^business/unfollow/$',
        'app.views.business.follow',
        {'subscribe': False},
    ),
    url(
        r'^business/profile/$',
        'app.views.business.edit_profile',
    ),
    url(
        r''.join([
            '^business/profile/set_primary_image/(?P<business_id>',
            REGEX_UUID,
            ')/(?P<image_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'app.views.business.set_primary_image'
    ),
    url(
        r''.join([
            '^business/profile/delete_image/(?P<business_id>',
            REGEX_UUID,
            ')/(?P<image_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'app.views.business.delete_image'
    ),
    url(
        r'^subscriptions/$',
        'app.views.business.subscriptions',
    ),
    url(
        r'^business/services/$',
        'app.views.business.services',
    ),
    url(
        r'^business/qrcode/$',
        'knotis_qrcodes.views.manage',
    ),
    url(
        r'^qrcode/(?P<qrcode_id>[^/]+)/$',
        'knotis_qrcodes.views.scan',
    ),
    url(
        r'^media/ajax/',
        'app.views.media.ajax'
    ),
    url(
        r'^media/(?P<path>.+)/$',
        'app.views.media.xsendfileserve', {
            'document_root': settings.MEDIA_ROOT
        },
    ),
    url(
        r'^auth/login/$',
        'knotis_auth.views.login',
    ),
    url(
        r'^facebook/login(/(?P<account_type>[^/]+))?/$',
        'knotis_auth.views.facebook_login',
    ),
    url(
        r'^auth/resend_validation_email/(?P<username>[^/]+)/$',
        'knotis_auth.views.resend_validation_email'
    ),
    url(
        r'^auth/logout/$',
        'knotis_auth.views.logout',
    ),
    url(
        r'^signup/(?P<account_type>[^/]+)*$',
        'knotis_auth.views.sign_up',
    ),
    url(
        r'^auth/validate/(?P<user_id>[^/]+)/(?P<validation_key>[^/]+)',
        'knotis_auth.views.validate',
    ),
    url(
        r'^forgotpassword/$',
        'knotis_auth.views.password_forgot',
    ),
    url(
        r'^passwordreset/(?P<validation_key>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
        'knotis_auth.views.password_reset',
    ),
    url(
        r'^passwordreset/$',
        'knotis_auth.views.password_reset',
    ),
    url(
        r'^neighborhood/(?P<city>[^/]+)*/$',
        'app.views.city.get_neighborhoods',
    ),
    url(
        r'^paypal/',
        include('paypal.urls')
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
        include('api.urls')
    ),
    url(
        r'^(?P<backend_name>[^/]+)/$',
        'app.views.business.profile',
    ),
)

urlpatterns += staticfiles_urlpatterns()
