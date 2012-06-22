from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication.oauth import OAuthAuthentication
from handlers.user import UserHandler
from handlers.endpoint import EndpointHandler

oauth = OAuthAuthentication(realm="Knotis")
AUTHENTICATORS = [oauth,]
handler_aguments = {'authentication': AUTHENTICATORS}

user_handler = Resource(UserHandler, **handler_aguments)
endpoint_handler = Resource(EndpointHandler, **handler_aguments)
urlpatterns = patterns('',
  url(r'^user/(?P<user_id>[^/]+)/', user_handler),
  url(r'^users/', user_handler),
  url(r'^endpoints/(?P<user_id>[^/]+)/', endpoint_handler),
)

# Django Piston OAuth
urlpatterns += patterns(
  'piston.authentication.oauth.views',
  url(r'^oauth/request_token/$','get_request_token'),
  url(r'^oauth/authorize/$','authorize_request_token'),
  url(r'^oauth/access_token/$','get_access_token'),
)

class CsrfExemptResource( Resource ):
    def __init__( self, handler, authentication = None ):
        super( CsrfExemptResource, self ).__init__( handler, authentication )
        self.csrf_exempt = getattr( self.handler, 'csrf_exempt', True )

from web.api.handlers.content import ContentHandler
content_handler = CsrfExemptResource(ContentHandler)

#content
urlpatterns += patterns(
   url(r'^content/write$', content_handler, { 'emitter_format': 'json' }),
   url(r'^content/(?P<content_id>[^/]+)/', content_handler),
   url(r'^content/', content_handler),
)
