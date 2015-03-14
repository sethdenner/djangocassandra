from django.conf.urls import (
    patterns,
    url,
)

from views import (
    MyFollowingView,
    ChangeFollowingView,
)

urlpatterns = patterns(
    '',
    url(
        r'^relation/following/',
        ChangeFollowingView.as_view()    
    ),
)




urlpatterns += MyFollowingView.urls()
