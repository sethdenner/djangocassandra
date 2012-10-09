from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import (
    REGEX_UUID,
    REGEX_OFFER_FILTERING,
)
from knotis.apps.offer.models import OfferSort


urlpatterns = patterns(
    'knotis.apps.offer.views',
    url(
        r''.join([
            'buy/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'purchase'
    ),
    url(
        r''.join([
            'delete/(?P<offer_id>',
            REGEX_UUID,
            ')/$'
        ]),
        'delete_offer'
    ),
    url(
        r''.join([
            '(?P<offer_id>',
            REGEX_UUID,
            ')/$',
        ]),
        'offer',
    ),
    url(
        r's/dashboard/$',
        'dashboard',
    ),
    url(
        's/print_unredeemed',
        'print_unredeemed',
    ),
    url(
        r's/get_user_offers/(?P<status>[\D]+)/$',
        'get_user_offers'
    ),
    url(
        r's/get_offers_by_status/(?P<status>[a-zA-Z_-]+)/$',
        'get_offers_by_status',
    ),
    url(
        r''.join([
            's/get_popular_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'get_available_offers',
        {'sort_by': OfferSort.POPULAR},
    ),
    url(
        r''.join([
            's/get_newest_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'get_available_offers',
        {'sort_by': OfferSort.NEWEST},
    ),
    url(
        r''.join([
            's/get_expiring_offers',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'get_available_offers',
        {'sort_by': OfferSort.EXPIRING},
    ),
    url(
        r's/update/(?P<offer_id>[^/]+)/$',
        'edit',
    ),
    url(
        r''.join([
            's/offer_map',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'offer_map',
    ),
    url(
        r''.join([
            's',
            REGEX_OFFER_FILTERING,
            '/$'
        ]),
        'offers',
    ),
    url(
        r'create/$',
        'edit',
    ),
)
