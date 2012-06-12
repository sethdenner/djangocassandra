from django.conf.urls.defaults import *
from piston.resource import Resource
# from piston.authentication import HttpBasicAuthentication
from web.api.handlers import UserHandler, EndpointHandler

# auth = HttpBasicAuthentication(realm="Django Piston Example")
user_handler = Resource(UserHandler) # , authentication=auth)
endpoint_handler = Resource(EndpointHandler)
urlpatterns = patterns('',
   url(r'^user/(?P<user_id>[^/]+)/', user_handler),
   url(r'^users/', user_handler),
   url(r'^endpoints/(?P<user_id>[^/]+)/', endpoint_handler)
)
