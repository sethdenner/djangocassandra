from django.conf.urls.defaults import (
    patterns,
    url

)

from views import (
    SearchResultsView,
    SearchResultsGrid
)

urlpatterns = patterns(
    'knotis.contrib.search.views',
    url(
        r'^search/grid/(?P<page>\d+)/(?P<count>\d+)/$',
        SearchResultsGrid.as_view()
    ),
)

urlpatterns += SearchResultsView.urls()
