from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(
        r'^(?P<login>(login)*)(/)*$',
        'app.views.home.index',
        name='home'
    ),
    url(
        r'^plans/$',
        'app.views.home.plans',
        name='home'
    ),
    url(
        r'^contact/$',
        'app.views.home.contact',
        name='home'
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
        r'^events/$',
        'app.views.events.events',
        name='events'
    ),
    url(
        r'^happyhours/$',
        'app.views.happy_hours.happy_hours',
        name='happy_hours'
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
        r'^offers/$',
        'app.views.offer.offers',
        name='offers'
    ),
    url(
        r'^offers/dashboard/$',
        'app.views.offer.dashboard',
        name='offers'
    ),
    url(
        r'^offers/get_offers_by_status/(?P<status>[^/]+)/$',
        'app.views.offer.get_offers_by_status',
        name='offers'
    ),
    url(
        r'^offers/offer_map/',
        'app.views.offer.offer_map',
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
        r'^business/offers/update/(?P<offer_id>[^/]+)/$',
        'app.views.offer.edit',
        name='business',
    ),
    url(
        r'^business/profile/$',
        'app.views.business.edit_profile',
        name='business'
    ),
    url(
        r'^subscriptions/$',
        'app.views.subscription.view',
        name='subscriptions'
    ),
    url(
        r'^business/qrcode/$',
        'app.views.business.qrcode',
        name='business'
    ),
    url(
        r'^business/tickets/$',
        'app.views.business.tickets',
        name='business'
    ),
    url(
        r'^qrcode/(?P<qrcode_id>[^/]+)/$',
        'app.views.qrcode.scan',
        name='qrcode'
    ),
    url(
        r'media/(?P<path>.+)/$',
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
        r'^passwordreset/$',
        'knotis_auth.views.password_reset',
        name='auth'
    ),
    url(
        r'^neighborhood/(?P<city>[^/]+)*/$',
        'app.views.city.get_neighborhoods',
        name='city'
    ),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(
        r'^(?P<backend_name>[^/]+)/$',
        'app.views.business.profile',
        name='business'
    ),
)

urlpatterns += staticfiles_urlpatterns()
