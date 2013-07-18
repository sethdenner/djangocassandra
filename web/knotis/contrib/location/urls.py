from django.conf.urls.defaults import patterns
from api import LocationApi

urlpatterns = patterns(
    'knotis.contrib.maps.views',
    LocationApi.urls()
)
