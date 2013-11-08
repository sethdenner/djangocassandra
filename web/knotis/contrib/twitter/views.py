import oauth2 as oauth
import urllib
import urllib2
import json
import time

from django.utils import log
logger = log.getLogger(__name__)

from django.conf import settings
from django.template import Context
from django.template.loader import get_template


def get_twitter_feed_json(
    twitter_id,
    count=settings.TWITTER_DEFAULT_RESULT_COUNT
):

    url = settings.TWITTER_FEED_URL
    parameters = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'include_entities': 'true',
        'include_rts': 'true',
        'screen_name': twitter_id,
        'count': count
    }

    token = oauth.Token(
        key=settings.TWITTER_KNOTIS_ACCESS_TOKEN,
        secret=settings.TWITTER_KNOTIS_TOKEN_SECRET
    )

    consumer = oauth.Consumer(
        key=settings.TWITTER_CONSUMER_KEY,
        secret=settings.TWITTER_CONSUMER_SECRET
    )

    parameters['oauth_token'] = token.key
    parameters['oauth_consumer_key'] = consumer.key

    request = oauth.Request(
        method='GET',
        url=url,
        parameters=parameters
    )

    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    request.sign_request(
        signature_method,
        consumer,
        token
    )

    client = oauth.Client(
        consumer,
        token
    )

    try:
        request_url = ''.join([
            request.normalized_url,
            '?',
            urllib.urlencode(
                request.get_nonoauth_parameters()
            )
        ])
        response, content = client.request(
            request_url,
            method=request.method,
            headers=request.to_header()
        )

    except Exception:
        logger.exception('failed to get twitter feed.')
        raise Error
        content = None

    return content


def get_twitter_feed_html(
    twitter_id,
    count=settings.TWITTER_DEFAULT_RESULT_COUNT
):    
    feed = get_twitter_feed(
        twitter_id,
        count
    )
    
    feed_template = get_template('tweet.html')

    context = Context({
        'feed': feed
    })
    return feed_template.render(context)
