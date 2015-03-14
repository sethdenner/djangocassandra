from django.conf.urls import patterns, include, url
from django.views.decorators.csrf import csrf_exempt


import util

urlpatterns = patterns('',
)

from django.http import HttpResponse

"""
Register all quick models in the admin.
"""

for m in util.get_quick_models():
    urlpatterns += patterns('',
        url(r'^'+str(m.__name__)+"$", lambda x: HttpResponse('<h1>'+str(m.__name__)+"</h1>")),
    )

from views import QuickView

for model_name in util.get_quick_model_names():
    urlpatterns += patterns('',
        #url(r'^(?P<model>' + model_name + r')(/(?P<pk>[-_\w]+))?/?$', QuickView.as_view(), name=model_name),
        #url(r'^(?P<model>' + model_name + r')(/(?P<pk>[-_\w]+))?/?$', csrf_exempt(QuickView.as_view()), name=model_name),
        url(r'^(?P<model>' + model_name + r')(/(?P<pk>[-_\w]+))?/?$', csrf_exempt(util.get_quick_view), name=model_name),
    )

# This method works nicely but breaks reverse url lookups.
#models_regex = '|'.join(util.get_quick_model_names())
#urlpatterns += patterns('',
#    url(r'^(?P<model>' + models_regex + r')(/(?P<pk>[-_\w]+))?/?$', QuickView.as_view()),
#)

#from views import dynamic
#for (name, view)  in dynamic.get_quick_views().iteritems():
#    print "registering admin for:" + str(view.__name__)
#    urlpatterns += patterns('',
#        url(r'^'+str(name)+"$", view.as_view(), name=view.__name__),
#    )

#urlpatterns += patterns('',
#    # Examples:
#    # url(r'^$', 'web.views.home', name='home'),
#    # url(r'^web/', include('web.foo.urls')),
#
#    # Uncomment the admin/doc line below to enable admin documentation:
#    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
#
#    # Uncomment the next line to enable the admin:
#)
