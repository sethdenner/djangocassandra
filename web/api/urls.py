from django.conf.urls.defaults import *
from piston.resource import Resource
# from piston.authentication import HttpBasicAuthentication
from web.api.handlers import AccountHandler

# auth = HttpBasicAuthentication(realm="Django Piston Example")
account_handler = Resource(AccountHandler) # , authentication=auth)
urlpatterns = patterns('',
   url(r'^account/(?P<post_slug>[^/]+)/', account_handler),
   url(r'^accounts/', account_handler),
)
