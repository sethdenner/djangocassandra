from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^$', 'web.app.views.home.index', name='home'),
  url(r'^business/create', 'web.app.views.business.create_business', name="business"),
  url(r'^business/list', 'web.app.views.business.list_businesses', name="business"),
  url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),
  url(r'^api/', include('web.api.urls')),
)

urlpatterns += staticfiles_urlpatterns()
