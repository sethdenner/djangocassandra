from django.utils.unittest import TestCase

from django.conf import settings
from django.test import Client

from .api import StripeApi

from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from knotis.contrib.offer.tests.utils import OfferTestUtils
from knotis.contrib.offer.models import Offer


class StripeApiTestCase(TestCase):
    def test_get_stripe_api_key(self):
        stripe_api_key = StripeApi.get_stripe_api_key()
        self.assertTrue(stripe_api_key)
        self.assertEqual(stripe_api_key, settings.STRIPE_API_SECRET)

    def test_get_purchase_parameters(self):
        class FakePurchaseRequest(object):
            def __init__(self):
                self.DATA = {
                    'stripeToken': 'faketoken',
                    'chargeAmount': '20.0',
                    'offerId': 'fake_offerid',
                    'quantity': '2',
                    'extra_param': 'foo',
                    'bar': 'blah'
                }

        request = FakePurchaseRequest()
        purchase_parameters = StripeApi.get_purchase_parameters(request)

        self.assertEqual(
            request.DATA['stripeToken'],
            purchase_parameters['token']
        )
        self.assertEqual(
            request.DATA['offerId'],
            purchase_parameters['offer_id']
        )
        self.assertEqual(
            float(request.DATA['chargeAmount']),
            purchase_parameters['amount']
        )
        self.assertEqual(
            float(request.DATA['quantity']),
            purchase_parameters['quantity']
        )
        self.assertEqual(len(purchase_parameters), 4)


class StripeViewTestCase(TestCase):
    def setUp(self):
        self.user_password = 'test_password'
        self.user, self.user_identity = UserCreationTestUtils.create_test_user(
            password=self.user_password
        )
        offer_collection = OfferTestUtils.create_test_offer_collection()
        self.offer = Offer.objects.get(description=offer_collection.pk)
        self.client = Client()
        login_args = {
            'username': self.user.username,
            'password': self.user_password
        }

        self.client.login(**login_args)

    def test_purchase(self):
        data = {
            'stripeToken': 'faketoken',
            'chargeAmount': '20.0',
            'offerId': str(self.offer.pk),
            'quantity': '1',
        }
        response = self.client.post('/stripe/charge/', data)
        self.assertEqual(response.status_code, 200)
