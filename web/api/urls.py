from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import OAuthAuthentication
from web.api.handlers import UserHandler, EndpointHandler

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
  'piston.authentication',
  url(r'^oauth/request_token/$','oauth_request_token'),
  url(r'^oauth/authorize/$','oauth_user_auth'),
  url(r'^oauth/access_token/$','oauth_access_token'),
)
