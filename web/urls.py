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
        r'^(?P<login>login)?(/)*$',
        'app.views.home.index',
        name='home'
    ),
    url(
        r'^plans/$',
        'app.views.home.plans',
        name='home'
    ),
    url(
        r'^contact',
        include('knotis_contact.urls'),
        name='contact'
    ),
    url(
        r'^about/$',
        'app.views.home.about',
        name='home'
    ),
    url(
        r'^howitworks/$',
        'app.views.home.how_it_works',
        name='home'
    ),
    url(
        r'^story/$',
        'app.views.home.story',
        name='home'
    ),
    url(
        r'^inquire/$',
        'app.views.home.inquire',
        name='home'
    ),
    url(
        r'^support/$',
        'app.views.home.support',
        name='home'
    ),
    url(
        r'^terms/$',
        'app.views.home.terms',
        name='home'
    ),
    url(
        r'^privacy/$',
        'app.views.home.privacy',
        name='home'
    ),
    url(
        r'^events',
        include('knotis_events.urls'),
        name='events'
    ),
    url(
        r'^happyhours',
        include('knotis_happyhour.urls'),
        name='happyhour'
    ),
    url(
        r'^dashboard',
        'app.views.dashboard.dashboard',
        name='dashboard'
    ),
    url(
        r'^offer/(?P<offer_id>[^/]+)/$',
        'app.views.offer.offer',
        name='offers'
    ),
    url(
        r'^offers/dashboard/$',
        'app.views.offer.dashboard',
        name='offers'
    ),
    url(
        r'^offers/get_offers_by_status/(?P<status>[a-zA-Z_-]+)/(?P<business_id>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})(/(?P<city>[a-zA-Z_-]+)(/(?P<neighborhood>[a-zA-Z_-]+))?)?(/(?P<category>[a-zA-Z_-]+))?(/(?P<premium>premium))?(/(?P<page>[\d]+))?/$',
        'app.views.offer.get_offers_by_status',
        name='offers'
    ),
    url(
        r''.join([
            '^offers/get_popular_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.get_available_offers',
        {'sort_by': OfferSort.POPULAR},
        name='offers'
    ),
    url(
        r''.join([
            '^offers/get_newest_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.get_available_offers',
        {'sort_by': OfferSort.NEWEST},
        name='offers'
    ),
    url(
        r''.join([
            '^offers/get_expiring_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.get_available_offers',
        {'sort_by': OfferSort.EXPIRING},
        name='offers'
    ),
    url(
        r'^offers/update/$',
        'app.views.offer.update',
        name='offers'
    ),
    url(
        r''.join([
            '^offers/offer_map',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.offer_map',
        name='offers'
    ),
    url(
        r''.join([
            '^offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'app.views.offer.offers',
        name='offers'
    ),
    url(
        r'^business/offers/create/$',
        'app.views.offer.edit',
        name='business'
    ),
    url(
        r'^profile/$',
        'app.views.user.profile',
        name='user'
    ),
    url(
        r'^profile/update/$',
        'app.views.user.profile_ajax',
        name='user'
    ),
    url(
        r'^business/offers/update/(?P<offer_id>[^/]+)/$',
        'app.views.offer.edit',
        name='business',
    ),
    url(
        r'^business/follow/$',
        'app.views.business.follow',
        {'subscribe': True},
        name='business'
    ),
    url(
        r'^business/unfollow/$',
        'app.views.business.follow',
        {'subscribe': False},
        name='business'
    ),
    url(
        r'^business/profile/$',
        'app.views.business.edit_profile',
        name='business'
    ),
    url(
        r'^subscriptions/$',
        'app.views.business.subscriptions',
        name='subscriptions'
    ),
    url(
        r'^business/services/$',
        'app.views.business.services',
        name='business'
    ),
    url(
        r'^business/qrcode/$',
        'knotis_qrcodes.views.manage',
        name='qrcodes'
    ),
    url(
        r'^qrcode/(?P<qrcode_id>[^/]+)/$',
        'knotis_qrcodes.views.scan',
        name='qrcodes'
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
        name='media'
    ),
    url(
        r'^auth/login/$',
        'knotis_auth.views.login',
        name='auth'
    ),
    url(
        r'^facebook/login(/(?P<account_type>[^/]+))?/$',
        'knotis_auth.views.facebook_login',
        name='auth'
    ),
    url(
        r'^auth/logout/$',
        'knotis_auth.views.logout',
        name='auth'
    ),
    url(
        r'^signup/(?P<account_type>[^/]+)*$',
        'knotis_auth.views.sign_up',
        name='auth'
    ),
    url(
        r'^auth/validate/(?P<user_id>[^/]+)/(?P<validation_key>[^/]+)',
        'knotis_auth.views.validate',
        name='auth'
    ),
    url(
        r'^forgotpassword/$',
        'knotis_auth.views.password_forgot',
        name='auth'
    ),
    url(
        r'^passwordreset/(?P<validation_key>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
        'knotis_auth.views.password_reset',
        name='auth'
    ),
    url(
        r'^passwordreset/$',
        'knotis_auth.views.password_reset',
        name='auth'
    ),
    url(
        r'^neighborhood/(?P<city>[^/]+)*/$',
        'app.views.city.get_neighborhoods',
        name='city'
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
        name='business'
    ),
)

urlpatterns += staticfiles_urlpatterns()
