# from django.test import TestCase
from unittest import TestCase

from knotis.contrib.identity.models import (
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment
)

from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from .utils import IdentityModelTestUtils


class IdentityModelTests(TestCase):

    def setUp(self):
        (
            self.user_consumer,
            self.identity_consumer
        ) = UserCreationTestUtils.create_test_user(
            first_name='Test',
            last_name='Consumer',
            email='testconsumer@example.com'
        )

        (
            self.user_merchant,
            self.identity_merchant
        ) = UserCreationTestUtils.create_test_user(
            first_name='Test',
            last_name='Merchant',
            email='testmerchant@example.com'
        )

        self.business, self.establishment = \
            IdentityModelTestUtils.create_test_business(
                self.identity_merchant,
                name='Test Business'
            )

    def test_individual(self):
        individual = IdentityIndividual.objects.get_individual(
            self.user_consumer
        )
        self.assertEqual(
            individual.name,
            self.identity_consumer.name
        )
        self.assertEqual(
            individual.description,
            self.identity_consumer.description
        )
        self.assertEqual(
            individual.identity_type,
            self.identity_consumer.identity_type
        )

    def test_business(self):
        businesses = IdentityBusiness.objects.get_businesses(
            self.identity_merchant
        )

        self.assertGreaterEqual(len(businesses), 1)

    def test_establishment(self):
        establishments_by_manager = (
            IdentityEstablishment.objects.get_establishments(
                self.identity_merchant
            )
        )
        establishments_by_business = (
            IdentityEstablishment.objects.get_establishments(
                self.business
            )
        )

        self.assertGreaterEqual(
            len(establishments_by_business),
            1
        )
        self.assertGreaterEqual(
            len(establishments_by_manager),
            1
        )

    def test_no_manager_status(self):
        self.assertFalse(self.identity_consumer.is_manager(self.establishment))

    def test_is_manager_status(self):
        self.assertFalse(self.identity_merchant.is_manager(self.establishment))
