from django.conf.urls.defaults import (
    patterns,
    url,
)

from django.contrib.auth.decorators import (
    login_required,
)

from knotis.contrib.activity.admin import (
    ActivityAdminView,
    ActivityAdminAJAXView,
)
from knotis.contrib.auth.admin import (
    UserAdminView,
    UserQueryAdminAJAXView,
    UserUpdateAdminAJAXView,
)

from views import (
    AdminDefaultView,
)

urlpatterns = patterns(
    '',
### ACTIVITY VIEWER
    url(
        r'^admin/activity/interact/$', login_required(ActivityAdminAJAXView.as_view())
    ),
    url(
        r'^admin/activity/$', login_required(ActivityAdminView.as_view())
    ),
### USER VIEWER
    url(
        r'^admin/user/interact/update-(?P<user_id>[a-zA-Z0-9\-]+)/$', login_required(UserUpdateAdminAJAXView.as_view())
    ),
    url(
        r'^admin/user/interact/$', login_required(UserQueryAdminAJAXView.as_view())
    ),
    url(
        r'^admin/user/$', login_required(UserAdminView.as_view())
    ),
### FALL THROUGH DEFAULT
    url(
        r'^admin/', login_required(AdminDefaultView.as_view())
    ),
)
