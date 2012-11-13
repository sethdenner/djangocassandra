from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID


urlpatterns = patterns(
    'knotis.apps.business.views',
    url(
        r'^business/follow/$',
        'follow',
        {'subscribe': True},
    ),
    url(
        r'^business/unfollow/$',
        'follow',
        {'subscribe': False},
    ),
    url(
        r'^business/profile/$',
        'edit_profile',
    ),
    url(
        r''.join([
            'profile/set_primary_image/(?P<business_id>',
            REGEX_UUID,
            ')/(?P<image_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'set_primary_image'
    ),
    url(
        r'^subscriptions/$',
        'subscriptions',
    ),
    url(
        r'^business/services/$',
        'services',
    ),
    url(
        r'^businesses/as_rows/((?P<page>[\d]+)/)?$',
        'get_business_rows'
    ),
)
