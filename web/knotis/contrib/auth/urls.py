from django.conf.urls.defaults import (
    patterns,
    url
)

from views import (
    LoginView,
    SignUpView
)

from views import (
    PasswordResetEmailBody,
    PasswordChangedEmailBody,
    ChangeEmailEmailBody,
    ChangedEmailEmailBody,
    WelcomeEmailBody
)

urlpatterns = patterns(
    'knotis.contrib.auth.views',

    url(
        r'^auth/login/$',
        LoginView.as_view()
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
)
