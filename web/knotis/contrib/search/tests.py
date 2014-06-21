from django.test import TestCase
from rest_framework.test import (
    APIClient,
    APITestCase
)


class SearchApiTest(TestCase):
    def setup(self):
        pass

    def test_class_definitions(self):
        from .api import SearchApi

    def test_offer_search(self):
        pass

    def test_identity_search(self):
        pass

    def test_business_search(self):
        pass

    def test_establishment_search(self):
        pass

    def test_individual_search(self):
        pass

    def test_transaction_search(self):
        pass


class SearchXapiViewTest(APITestCase):
    def setup(self):
        pass

    def test_class_definitions(self):
        from .api import SearchApiViewSet

    def test_search_query(self):
        client = APIClient()
        response = client.get('/api/v0/search/?q=testing')

    def test_forbidden_requests(self):
        pass
