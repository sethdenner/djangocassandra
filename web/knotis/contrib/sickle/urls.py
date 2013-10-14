from django.conf.urls.defaults import patterns, url

from knotis.utils.regex import REGEX_UUID

urlpatterns = patterns(
    'knotis.contrib.sickle.views',
    url(
        r''.join([
            'image/crop/(?P<image_id>',
            REGEX_UUID,
            ')/(?P<related_object_id>',
            REGEX_UUID,
            ')/((?P<context>\w{1,16})/)?((?P<image_max_width>[\d]+)/(?P<image_max_height>[\d]+)/)?$'
        ]),
        'crop'
    )
)
