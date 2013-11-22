from django.conf.urls.defaults import (
    patterns,
    url

)
from django.views.generic.simple import redirect_to

from knotis.utils.regex import REGEX_UUID

from views import (
    SearchResultsView
)

from api import (
    SearchApi,
)

urlpatterns = patterns(
    'knotis.contrib.search.views',
    url(
        r'^search/',
        SearchResultsView.as_view()
    ),
    SearchApi.urls(),
)
