from django.conf.urls.defaults import patterns, url
from api import LocationApi
from views import LocationFormView

urlpatterns = patterns(
    'knotis.contrib.maps.views',
    LocationApi.urls(),
    url(
        r'^location_form/$', 
        LocationFormView.as_view()
    )
)
