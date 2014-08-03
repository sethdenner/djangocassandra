from django.conf.urls.defaults import (
    patterns,
    url,
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
    AdminValidateResendView,
	AdminOwnerView,
)

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
        r''.join([
	        '^admin/utils/ident_pass_reset/(?<identity_id>',
			REGEX_UUID,
			')/$'
		]), AdminValidateResentView.as_view()
    ),
)


urlpatterns += AdminOwnerView.urls()