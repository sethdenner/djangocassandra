from django.conf.urls.defaults import (
    patterns,
    url
)

from views import (
    LoginView,
    SignUpView
)
from api import (
    AuthUserApi,
    AuthenticationApi
)

urlpatterns = patterns(
    'knotis.contrib.auth.views',
    AuthUserApi.urls(),
    AuthenticationApi.urls(),
    url(
        r'^auth/login/$',
        LoginView.as_view()
    ),
    url(
        r'^auth/resend_validation_email/(?P<username>[^/]+)/$',
        'resend_validation_email'
    ),
    url(
        r'^auth/logout/$',
        'logout',
    ),
    url(
        r'^auth/signup/(?P<account_type>[^/]+)*$',
        SignUpView.as_view()
    ),
    url(
        r'^auth/validate/(?P<user_id>[^/]+)/(?P<validation_key>[^/]+)',
        'validate',
    ),
    url(
        r'^forgotpassword/$',
        'password_forgot',
    ),
    url(
        r'^passwordreset/(?P<validation_key>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
        'password_reset',
    ),
    url(
        r'^passwordreset/$',
        'password_reset',
    ),
    url(
        r'^plans/$',
        'plans',
    ),
    url(
        r'^profile/$',
        'profile',
    ),
    url(
        r'^profile/update/$',
        'profile_ajax',
    ),
)
