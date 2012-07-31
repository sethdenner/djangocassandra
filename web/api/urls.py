from api.handlers.business import BusinessModelHandler
from api.handlers.content import ContentHandler
from api.handlers.establishment import EstablishmentModelHandler
from api.handlers.testmodel import TestModelHandler
from django.conf.urls.defaults import patterns, url, include
from handlers.endpoint import EndpointHandler
from handlers.user import UserHandler
from piston.authentication.oauth import OAuthAuthentication
from piston.resource import Resource
oauth = OAuthAuthentication(realm="Knotis")
AUTHENTICATORS = [oauth, ]
handler_arguments = {'authentication': AUTHENTICATORS}

user_handler = Resource(UserHandler, **handler_arguments)
endpoint_handler = Resource(EndpointHandler, **handler_arguments)
establishment_handler = Resource(EstablishmentModelHandler)
business_handler = Resource(BusinessModelHandler)
urlpatterns = patterns('',
  url(r'^user/(?P<user_id>[^/]+)/', user_handler),
  url(r'^users/', user_handler),
  url(r'^endpoints/(?P<user_id>[^/]+)/', endpoint_handler),
  url(r'^establishments', establishment_handler),
  url(r'^businesses', business_handler),
  url(r'^business/(?P<id>[^/]+)/', business_handler),
  url(r'^business/create/', business_handler, {'emitter_format': 'json'})
)


class CsrfExemptResource(Resource):
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

content_handler = CsrfExemptResource(ContentHandler)

urlpatterns += patterns('',
    url(r'^oauth/callback', 'app.views.authentication.oauth_callback'),
    url(r'^oauth/', include('piston.authentication.oauth.urls')),
)

#content
urlpatterns += patterns(
   url(r'^content/write$', content_handler, {'emitter_format': 'json'}),
   url(r'^content/(?P<content_id>[^/]+)/', content_handler),
   url(r'^content/', content_handler),
)

testmodel_handler = CsrfExemptResource(TestModelHandler)

#content
urlpatterns += patterns(
   url(r'^testmodel/write$', testmodel_handler, {'emitter_format': 'json'}),
   url(r'^testmodel/(?P<testmodel_id>[^/]+)/', testmodel_handler),
   url(r'^testmodel/', testmodel_handler),
)
