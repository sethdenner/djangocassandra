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

from admin import (
    EditUserModal,
)

urlpatterns = patterns(
    'knotis.contrib.auth.views',
    url(
        r'^auth/logout/$',
        'logout',
    ),
    url(
        r'^auth/validate/(?P<user_id>[^/]+)/(?P<validation_key>[^/]+)',
        'validate',
    ),
    url(
        r'^auth/resend_validation_email/(?P<username>[^/]+)/$',
        'resend_validation_email'
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

urlpatterns += LoginView.urls()
urlpatterns += SignUpView.urls()
urlpatterns += SignUpSuccessView.urls()
urlpatterns += EditUserModal.urls()
