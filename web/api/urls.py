"""
from api.handlers.authentication import AuthenticationHandler
from api.handlers.business import BusinessModelHandler
from api.handlers.content import ContentHandler
from api.handlers.establishment import EstablishmentModelHandler
from api.handlers.testmodel import TestModelHandler
from handlers.endpoint import EndpointHandler
from handlers.user import UserHandler
from resource import JsonResource
"""

from django.conf.urls.defaults import patterns, url, include

from piston.authentication.oauth import OAuthAuthentication
from piston.resource import Resource
from api.handlers.media import ImageModelHandler

oauth_three_legged = OAuthAuthentication(realm='knotis')
oauth_two_legged = OAuthAuthentication(realm='knotis', two_legged=True)


image_handler = Resource(ImageModelHandler, authentication=oauth_two_legged)

urlpatterns = patterns('',
    url(
        r'^media/image/create/$',
        image_handler
    ),
    url(
        r'^oauth/',
        include('piston.authentication.oauth.urls')
    )
)

"""
user_handler = Resource(UserHandler, **handler_arguments)
endpoint_handler = Resource(EndpointHandler, **handler_arguments)
establishment_handler = Resource(EstablishmentModelHandler)
business_handler = Resource(BusinessModelHandler)
urlpatterns = patterns('',
    url(r'^auth/signup/', authentication_handler, { 'emitter_format': 'json' }),
    url(r'^user/(?P<user_id>[^/]+)/', user_handler),
    url(r'^users/', user_handler),
    url(r'^endpoints/(?P<user_id>[^/]+)/', endpoint_handler),
    url(r'^establishments', establishment_handler),
    url(r'^businesses', business_handler),
    url(r'^business/(?P<id>[^/]+)/', business_handler),
    url(r'^business/create/', business_handler, { 'emitter_format': 'json' }),
    url(r'^business/update/', business_handler, { 'emitter_format': 'json' })
)


class CsrfExemptResource(Resource):
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

content_handler = CsrfExemptResource(ContentHandler)

urlpatterns += patterns('',
    url(r'^oauth/', include('piston.authentication.oauth.urls')),
)

#content
urlpatterns += patterns(
   url(r'^content/write$', content_handler, {'emitter_format': 'json'}),
   # url(r'^content/(?P<content_id>[^/]+)/', content_handler),
   # url(r'^content/(?P<template_name>[^/]+)/', content_handler),
   url(r'^content/(?P<content_id>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$', content_handler),
   url(r'^content/(?P<template_name>.+)/$', content_handler),
   url(r'^content/$', content_handler),
)

testmodel_handler = CsrfExemptResource(TestModelHandler)

#content
urlpatterns += patterns(
   url(r'^testmodel/write$', testmodel_handler, {'emitter_format': 'json'}),
   url(r'^testmodel/(?P<testmodel_id>[^/]+)/', testmodel_handler),
   url(r'^testmodel/', testmodel_handler),
)

"""
