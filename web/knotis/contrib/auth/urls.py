from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

from views import (
    LoginView,
    SignUpView,
    SignUpSuccessView,
    ForgotPasswordView,
    ForgotPasswordSuccessView,
    ResetPasswordView
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
        r'^auth/signup/success/$',
        SignUpSuccessView.as_view()
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
        r'^auth/forgot/success/$',
        ForgotPasswordSuccessView.as_view()
    ),
    url(
        r'^auth/forgot/$',
        ForgotPasswordView.as_view()
    ),
    url(
        r''.join([
            '^auth/reset/(?P<user_id>',
            REGEX_UUID,
            ')/(?P<password_reset_key>',
            REGEX_UUID,
            ')/$'
        ]),
        ResetPasswordView.as_view()
    )
)
