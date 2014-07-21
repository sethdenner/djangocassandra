from django.conf.urls.defaults import (
    patterns,
    url,
)

from django.contrib.auth.decorators import (
    login_required,
)

from knotis.contrib.offer.admin import (
    OfferAdminView,
    OfferQueryAdminAJAXView,
)
from knotis.contrib.activity.admin import (
    ActivityAdminView,
    ActivityQueryAdminAJAXView,
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
### OFFER VIEWER
    url(
        r'^admin/offer/query/$', login_required(OfferQueryAdminAJAXView.as_view())
    ),
    url(
        r'^admin/offer/?$', login_required(OfferAdminView.as_view())
    ),
### ACTIVITY VIEWER
    url(
        r'^admin/activity/query/$', login_required(ActivityQueryAdminAJAXView.as_view())
    ),
    url(
        r'^admin/activity/?$', login_required(ActivityAdminView.as_view())
    ),
### USER VIEWER
    url(
        r'^admin/user/interact/update-(?P<user_id>[a-zA-Z0-9\-]+)/$', login_required(UserUpdateAdminAJAXView.as_view())
    ),
    url(
        r'^admin/user/query/$', login_required(UserQueryAdminAJAXView.as_view())
    ),
    url(
        r'^admin/user/?$', login_required(UserAdminView.as_view())
    ),
### FALL THROUGH DEFAULT
    url(
        r'^admin/', login_required(AdminDefaultView.as_view())
    ),
)
