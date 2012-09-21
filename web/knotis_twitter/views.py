import urllib2 as urllib
import json

from django.conf import settings
from django.template import Context,Template
from django.template.loader import get_template


def get_twitter_feed(
    twitter_id,
    count=settings.TWITTER_DEFAULT_RESULT_COUNT
):
    uri = settings.TWITTER_FEED_URI_TEMPLATE % (
        twitter_id,
        count 
    )
    
    try:
        connection = urllib.urlopen(
            uri,
            None
        )
        try:
            response = json.loads(connection.read())
        finally:
            connection.close()
    except urllib.HTTPError, error:
        response = json.loads(error.read())
    
    return response


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
    