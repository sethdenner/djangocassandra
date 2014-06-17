import twitter
import urllib
import time
import oauth2 as oauth

from django.utils import log
logger = log.getLogger(__name__)

from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import iri_to_uri
from django.shortcuts import get_object_or_404

from knotis.views import (
    AJAXFragmentView,
    AJAXView
)

from knotis.contrib.identity.models import Identity
from knotis.contrib.endpoint.models import EndpointTypes
from knotis.contrib.endpoint.forms import (
    EndpointForm,
    CredentialsForm
)
from knotis.contrib.endpoint.views import SocialIntegrationTile


class TwitterVerifyPINView(AJAXFragmentView):
    view_name = 'twitter_pin_entry'
    template_name = 'knotis/twitter/verify_pin.html'

    def process_context(self):
        request = self.context['request']

        self.context['oauth_token'] = request.GET.get('oauth_token')
        self.context['oauth_token_secret'] = request.GET.get(
            'oauth_token_secret'
        )

        return self.context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_object_or_404(
            Identity,
            pk=request.session['current_identity']
        )

        errors = {}
        verification_pin = request.POST.get('vpin')
        oauth_token = request.POST.get('oauth_token')
        oauth_token_secret = request.POST.get('oauth_token_secret')
        if not verification_pin:
            errors['vpin'] = 'No verification PIN provided'

        if not oauth_token:
            errors['oauth_token'] = 'No OAuth request token provided.'

        if not oauth_token_secret:
            errors['oauth_token_secret'] = (
                'No OAuth request token secret provided.'
            )

        if errors:
            return self.generate_response({
                'status': 'ERROR',
                'errors': errors
            })

        t = twitter.Twitter(
            auth=twitter.OAuth(
                oauth_token,
                oauth_token_secret,
                settings.TWITTER_CONSUMER_KEY,
                settings.TWITTER_CONSUMER_SECRET
            ),
            format='',
            api_version=None
        )

        try:
            oauth_token, oauth_token_secret = parse_oauth_tokens(
                t.oauth.access_token(oauth_verifier=verification_pin)
            )

        except Exception, e:
            return self.generate_response({
                'status': 'ERROR',
                'errors': {
                    'no-field': e.message
                }
            })

        if not oauth_token or not oauth_token_secret:
            return self.generate_response({
                'status': 'ERROR',
                'errors': {
                    'no-field': 'Something went wrong. Please contact support.'
                }
            })

        t = twitter.Twitter(
            auth=twitter.OAuth(
                oauth_token,
                oauth_token_secret,
                settings.TWITTER_CONSUMER_KEY,
                settings.TWITTER_CONSUMER_SECRET
            ),
            format='json',
            api_version='1.1'
        )

        endpoint_form = EndpointForm(
            data={
                'endpoint_type': EndpointTypes.TWITTER,
                'identity': current_identity.pk,
                'value': ''.join([
                    '@',
                    t.account.settings()['screen_name']
                ]),
                'context': 'twitter_publish',
                'primary': True,
                'validated': True
            }
        )

        if not endpoint_form.is_valid():
            errors = {}
            for field, messages in endpoint_form.errors.iteritems():
                errors[field] = [message for message in messages]
            return self.generate_response({
                'status': 'ERROR',
                'errors': errors
            })

        endpoint = endpoint_form.save()

        credentials_form = CredentialsForm(
            data={
                'endpoint': endpoint.pk,
                'identifier': oauth_token,
                'key': oauth_token_secret
            }
        )

        if not credentials_form.is_valid():
            endpoint.delete()

            errors = {}
            for field, messages in endpoint_form.errors.iteritems():
                errors[field] = [message for message in messages]
            return self.generate_response({
                'status': 'ERROR',
                'errors': errors
            })

        credentials_form.save()

        twitter_tile = SocialIntegrationTile(
            service='twitter',
            endpoint=endpoint
        )

        return self.generate_response({
            'status': 'OK',
            'errors': None,
            'html': twitter_tile.render_template_fragment(Context({
                'STATIC_URL': settings.STATIC_URL
            }))
        })


class TwitterGetAuthorizeUrl(AJAXView):
    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        consumer_key = settings.TWITTER_CONSUMER_KEY
        consumer_secret = settings.TWITTER_CONSUMER_SECRET
        t = twitter.Twitter(
            auth=twitter.OAuth(
                '',
                '',
                consumer_key,
                consumer_secret
            ),
            format='',
            api_version=None
        )

        oauth_token, oauth_token_secret = parse_oauth_tokens(
            t.oauth.request_token()
        )

        url = settings.TWITTER_AUTHORIZE_URL + oauth_token

        return self.generate_response({
            'authorize_url': url,
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret
        })


def parse_oauth_tokens(result):
    for r in result.split('&'):
        k, v = r.split('=')
        if k == 'oauth_token':
            oauth_token = v
        elif k == 'oauth_token_secret':
            oauth_token_secret = v
    return oauth_token, oauth_token_secret


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
        'screen_name': iri_to_uri(twitter_id),
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
        content = None

    return content


def get_twitter_feed_html(
    twitter_id,
    count=settings.TWITTER_DEFAULT_RESULT_COUNT
):
    feed = get_twitter_feed_json(
        twitter_id,
        count
    )

    feed_template = get_template('tweet.html')

    context = Context({
        'feed': feed
    })
    return feed_template.render(context)
