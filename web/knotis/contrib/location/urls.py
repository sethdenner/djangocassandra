from django.conf.urls.defaults import patterns, url

from views import LocationFormView

urlpatterns = patterns(
    '',
    url(
        r'^location_form/$', 
        LocationFormView.as_view()
    )
)
