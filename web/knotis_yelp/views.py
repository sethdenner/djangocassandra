import oauth2 as oauth
import urllib2 as urllib
import json

from django.conf import settings


def get_reviews_by_yelp_id(yelp_id):
    uri = ''.join([
        settings.YELP_API_URI,
        yelp_id
    ])
    consumer_key = settings.YELP_CONSUMER_KEY
    consumer_secret = settings.YELP_CONSUMER_SECRET
    token_key = settings.YELP_TOKEN_KEY
    token_secret = settings.YELP_TOKEN_SECRET

    consumer = oauth.Consumer(
        key=consumer_key,
        secret=consumer_secret
    )
    token = oauth.Token(
        key=token_key,
        secret=token_secret
    )

    parameters = {
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': oauth.generate_timestamp(),
        'oauth_token': token.key,
        'oauth_consumer_key': consumer.key,
    }

    request = oauth.Request(
        method='GET',
        url=uri,
        parameters=parameters
    )
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    request.sign_request(
        signature_method,
        consumer,
        token
    )
    signed_uri = request.to_url()

    try:
        connection = urllib.urlopen(
            signed_uri,
            None
        )
        try:
            response = json.loads(connection.read())
        finally:
            connection.close()
    except urllib.HTTPError, error:
        response = json.loads(error.read())

    return response['reviews']
