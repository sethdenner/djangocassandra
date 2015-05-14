from django.utils import unittest
from django.test.client import Client

class SimpleTest(unittest.TestCase):
    # How to define custom fixtures for tests
    #fixtures = ['mammals.json', 'birds']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        response = self.client.get('/product')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 5 customers.
        #self.assertEqual(len(response.context['customers']), 5)