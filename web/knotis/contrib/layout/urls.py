from django.conf.urls.defaults import (
    patterns, 
    url
)

from views import IndexView

urlpatterns = patterns(
    'knotis.contrib.layout.views',
    url(
        r'',
        IndexView.as_view()
    )
)
