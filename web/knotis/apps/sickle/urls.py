from django.conf.urls.defaults import patterns, url

from knotis.utils.regex import REGEX_UUID

urlpatterns = patterns(
    'knotis.apps.sickle.views',
    url(
        r''.join([
            'image/crop/(?P<image_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'crop'
    )
    
)