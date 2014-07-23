from django.conf.urls.defaults import (
    patterns,
    url
)

from views import (
    NewPermissionEmailBody,
    NewFollowerEmailBody,
    MyFollowingView
)


urlpatterns = patterns(
    'knotis.contrib.relation.views',
)

urlpatterns += MyFollowingView.urls()
