"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
# from django.test import TestCase
import oauth2 as oauth
from django.test import TestCase
from piston.models import Consumer, Token
from django.contrib.sites.models import Site
import settings

class OAuthTest(TestCase):
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    callback_url = 'http://127.0.0.1:8000/api/oauth/callback'
    request_token_url = 'http://127.0.0.1:8000/api/oauth/get_request_token'
    authorize_url = 'http://127.0.0.1:8000/api/oauth/authorize_request_token'
    access_token_url = 'http://127.0.0.1:8000/api/oauth/get_access_token'
    two_legged_api_url = 'http://127.0.0.1:8000/api/oauth/two_legged_api'
    three_legged_api_url = 'http://127.0.0.1:8000/api/oauth/three_legged_api'

    def setUp(self):
        super(OAuthTest, self).setUp()

        Site(id=settings.SITE_ID, domain="localhost", name="django-testapp").save() 
               
        self.consumer = Consumer.objects.create_consumer('Test Consumer')
        self.consumer.status = 'accepted'
        self.consumer.save()

    def tearDown(self):
        super(OAuthTest, self).tearDown()
        
        Site.objects.get(pk=settings.SITE_ID).delete()
        #self.consumer.delete()

    def test_get_request_token(self, callback='oob'):
        request = oauth.Request.from_consumer_and_token(self.consumer, None, 'GET', self.request_token_url, {'oauth_callback': callback})
        request.sign_request(self.signature_method, self.consumer, None)

        response = self.client.get(self.request_token_url, request)
        self.assertEquals(response.status_code, 200)

        params = dict(urlparse.parse_qsl(response.content))
        return oauth.Token(params['oauth_token'], params['oauth_token_secret'])

    def authorize_request_token(self, request_token_key):
        self.client.login(username='admin', password='admin')
        return self.client.post(self.authorize_url, {'oauth_token': request_token_key, 'authorize_access': None})

    def test_authorize_request_token_without_callback(self):
        request_token = self.test_get_request_token('oob')
        response = self.authorize_request_token(request_token.key)

        self.assertEquals(response.status_code, 200)

    def test_authorize_request_token_with_callback(self):
        request_token = self.test_get_request_token(self.callback_url)
        response = self.authorize_request_token(request_token.key)

        self.assertEquals(response.status_code, 302)
        self.assert_(response['Location'].startswith(self.callback_url))

    def test_get_access_token(self):
        request_token = self.test_get_request_token(self.callback_url)
        response = self.authorize_request_token(request_token.key)
        params = dict(urlparse.parse_qsl(response['Location'][len(self.callback_url)+1:]))
        
        request_token.set_verifier(params['oauth_verifier'])
        
        request = oauth.Request.from_consumer_and_token(self.consumer, request_token, 'POST', self.access_token_url)
        request.sign_request(self.signature_method, self.consumer, request_token)

        response = self.client.post(self.access_token_url, request)
        self.assertEquals(response.status_code, 200)
        
        params = dict(urlparse.parse_qsl(response.content))
        return oauth.Token(params['oauth_token'], params['oauth_token_secret'])

    def test_two_legged_api(self):
        request = oauth.Request.from_consumer_and_token(self.consumer, None, 'GET', self.two_legged_api_url, {'msg': 'expected response'})
        request.sign_request(self.signature_method, self.consumer, None)

        response = self.client.get(self.two_legged_api_url, request)
        self.assertEquals(response.status_code, 200)
        self.assert_('expected response' in response.content)

    def test_three_legged_api(self):
        access_token = self.test_get_access_token()

        request = oauth.Request.from_consumer_and_token(self.consumer, access_token, 'GET', self.three_legged_api_url, {'msg': 'expected response'})
        request.sign_request(self.signature_method, self.consumer, access_token)

        response = self.client.get(self.three_legged_api_url, request)
        self.assertEquals(response.status_code, 200)
        self.assert_('expected response' in response.content)
