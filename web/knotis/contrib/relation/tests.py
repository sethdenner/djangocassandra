from django.utils import unittest

from knotis.contrib.auth.tests import UserCreationTests
from knotis.contrib.identity.models import (
    IdentityBusiness,
    IdentityEstablishment
)
from knotis.contrib.relation.models import Relation


class RelationTests(unittest.TestCase):
    def setUp(self):
        (
            self.user_merchant,
            self.identity_merchant
        ) = UserCreationTests.create_test_user(
            first_name='Test',
            last_name='Merchant',
            email='testmerchant@example.com'
        )
        (
            self.user_consumer,
            self.identity_consumer
        ) = UserCreationTests.create_test_user(
            first_name='Test',
            last_name='Consumer',
            email='testconsumer@example.com'
        )

        self.business = IdentityBusiness.objects.create(
            self.identity_merchant,
            name='Test Business'
        )

        self.establishment = IdentityEstablishment.objects.create(
            self.business,
            name='Test Establishment'
        )

    def test_individual_relation(self):
        relation_merchant = Relation.objects.get_individual(
            self.user_merchant
        )
        relation_consumer = Relation.objects.get_individual(
            self.user_consumer
        )

        self.assertEqual(
            relation_merchant.subject_object_id,
            self.user_merchant.id
        )
        self.assertEqual(
            relation_merchant.related_object_id,
            self.identity_merchant.id
        )
        self.assertEqual(
            relation_consumer.subject_object_id,
            self.user_consumer.id
        )
        self.assertEqual(
            relation_consumer.related_object_id,
            self.identity_consumer.id
        )

    def test_manager_relation(self):
        relations_managed = Relation.objects.get_managed(
            self.identity_merchant
        )

        self.assertEqual(1, relations_managed.count())
        managed = relations_managed[0]
        self.assertEqual(
            self.identity_merchant.id,
            managed.subject_object_id
        )
        self.assertEqual(
            self.business.id,
            managed.related_object_id
        )

    def test_establishment_relation(self):
        relations_establishment = Relation.objects.get_establishments(
            self.business
        )

        self.assertEqual(1, relations_establishment.count())
        establishment = relations_establishment[0]
        self.assertEqual(
            self.business.id,
            establishment.subject_object_id
        )
        self.assertEqual(
            self.establishment.id,
            establishment.related_object_id
        )

    def test_following_relation(self):
        following = Relation.objects.create_following(
            self.identity_consumer,
            self.business
        )

        relations_following = Relation.objects.get_following(
            self.identity_consumer
        )

        self.assertEqual(1, relations_following.count())
        following = relations_following[0]
        self.assertEqual(
            self.identity_consumer.id,
            following.subject_object_id
        )
        self.assertEqual(
            self.business.id,
            following.related_object_id
        )
