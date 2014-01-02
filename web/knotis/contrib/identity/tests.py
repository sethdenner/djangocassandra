from django.test import TestCase

from knotis.contrib.auth.tests import UserCreationTests
from models import (
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment
)


class IdentityModelTests(TestCase):
    @staticmethod
    def create_test_individual(**kwargs):
        if not kwargs.get('name'):
            kwargs['name'] = 'Test Individual'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Individual description.'

        return IdentityIndividual.objects.create(**kwargs)

    @staticmethod
    def create_test_business(
        manager,
        **kwargs
    ):
        if not kwargs.get('name'):
            kwargs['name'] = 'Test Business'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Business description.'

        return IdentityBusiness.objects.create(
            manager,
            **kwargs
        )

    @staticmethod
    def create_test_establishment(
        business,
        **kwargs
    ):
        if not kwargs.get('name'):
            kwargs['name'] = 'Test Establishment'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Establishment description.'

        return IdentityEstablishment.objects.create(
            business,
            **kwargs
        )

    def setUp(self):
        (
            self.user_consumer,
            self.identity_consumer
        ) = UserCreationTests.create_test_user(
            first_name='Test',
            last_name='Consumer',
            email='testconsumer@example.com'
        )

        (
            self.user_merchant,
            self.identity_merchant
        ) = UserCreationTests.create_test_user(
            first_name='Test',
            last_name='Merchant',
            email='testmerchant@example.com'
        )

        self.business = IdentityBusiness.objects.create(
            self.identity_merchant,
            name='Test Business'
        )

        self.establishment = IdentityEstablishment.objects.create(
            self.business,
            name='Test Establishment'
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

        self.assertEqual(1, len(businesses))
        business = businesses[0]
        self.assertEqual(business.id, self.business.id)

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

        self.assertEqual(
            1,
            len(establishments_by_manager)
        )
        self.assertEqual(
            1,
            len(establishments_by_business)
        )
        self.assertEqual(
            self.establishment.id,
            establishments_by_manager[0].id,
        )
        self.assertEqual(
            self.establishment.id,
            establishments_by_business[0].id
        )


class IdentityViewTests(TestCase):
    def setUp(self):
        self.user_password = 'test_password'
        self.user, self.user_identity = UserCreationTests.create_test_user(
            password=self.user_password
        )

    def test_identity_switcher_view(self):
        self.client.login(
            username=self.user.username,
            password=self.user_password
        )
        response = self.client.get('/identity/switcher/')
        self.assertEqual(response.status_code, 200)

    def test_identity_switcher_fragment(self):
        pass
