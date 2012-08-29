from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from knotis_auth.views import KnotisAuthenticationForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<login>(login)*)(/)*$', 'app.views.home.index', name='home'),
    url(r'^plans/$', 'app.views.account.plans', name='account'),
    url(r'^business/create', 'app.views.business.create_business', name='business'),
    url(
        r'^login_popup/$', 
        'django.contrib.auth.views.login', {
            'template_name': 'login.html', 
            'authentication_form': KnotisAuthenticationForm
        },
        name='auth'
    ),
    url(
        r'^signup/(?P<account_type>[^/]+)$', 
        'knotis_auth.views.sign_up', 
        name='auth'
    ),
    url(
        r'^validate/(?P<user_id>[^/]+)/(?P<validation_key>[^/]+)', 
        'knotis_auth.views.validate', 
        name='auth'
    ),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
)

urlpatterns += staticfiles_urlpatterns()
