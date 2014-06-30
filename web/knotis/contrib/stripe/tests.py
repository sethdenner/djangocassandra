from django.utils.unittest import TestCase

from django.conf import settings

from .api import StripeApi


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
