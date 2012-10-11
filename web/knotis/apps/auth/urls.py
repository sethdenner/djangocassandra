from django.conf.urls.defaults import (
    patterns,
    url
)


'''

Here's the old facebook auth urls in case we ever want to hook this back up.

-Seth
                       
url(
    r'^auth/login/facebook(/(?P<account_type>[^/]+))?/$',
    'facebook_login',
),

'''
urlpatterns = patterns(
    'knotis.apps.auth.views',
    url(
        r'^auth/login/$',
        'login',
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
        'sign_up',
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
