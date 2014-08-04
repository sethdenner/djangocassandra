from django.conf.urls.defaults import (
    patterns,
    url,
)

from django.contrib.auth.decorators import (
    login_required,
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
    AdminValidateResendView,
    AdminOwnerView,
)

from knotis.utils.regex import REGEX_UUID

urlpatterns = patterns(
    '',
### ACTIVITY VIEWER
### App temporarily unlinked because of bugs.
#    url(
#        r'^admin/activity/interact/$', ActivityAdminAJAXView.as_view()
#    ),
#    url(
#        r'^admin/activity/$', ActivityAdminView.as_view()
#    ),
### USER VIEWER
#    url(
#        r'^admin/user/interact/update-(?P<user_id>[a-zA-Z0-9\-]+)/$', UserUpdateAdminAJAXView.as_view()
#    ),
#    url(
#        r'^admin/user/interact/$', UserQueryAdminAJAXView.as_view()
#    ),
#    url(
#        r'^admin/user/$', UserAdminView.as_view()
#    ),

### ADMIN RESEND URL
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
        r''.join([
            '^admin/utils/ident_pass_reset/(?P<identity_id>',
            REGEX_UUID,
            ')/$'
        ]), AdminValidateResendView.as_view()
    ),
)

urlpatterns += AdminOwnerView.urls()
