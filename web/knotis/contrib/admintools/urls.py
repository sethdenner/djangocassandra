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
    OfferUpdateAdminAJAXView,
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
    AdminBecomeManagerButton,
    AdminValidateResendView,
    AdminOwnerView,
    AdminDefaultView,
)

from knotis.utils.regex import REGEX_UUID

urlpatterns = patterns(
    '',
### ESTABLISHMENT MANAGER TOOLS
    url(
        r'^admin/utils/become_manager/',
        login_required(AdminBecomeManagerButton.as_view())
    ),
### OFFER VIEWER
    url(
        r'^admin/offer/update/$', login_required(OfferUpdateAdminAJAXView.as_view())
    ),
    url(
        r'^admin/offer/query/$', login_required(OfferQueryAdminAJAXView.as_view())
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

### ADMIN RESEND URL
    url(
        r''.join([
            '^admin/utils/ident_pass_reset/(?P<identity_id>',
            REGEX_UUID,
            ')/$'
        ]), AdminValidateResendView.as_view()
    ),
)
### OFFER VIEWER
urlpatterns += OfferAdminView.urls()

### ADMIN UTILITY FRAGMENTS AND MODALS
urlpatterns += AdminOwnerView.urls()

### ADMIN TOOL GRID VIEW
urlpatterns += AdminDefaultView.urls()
