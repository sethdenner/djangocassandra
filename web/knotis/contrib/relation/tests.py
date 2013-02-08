from django.test import unittest

from knotis.contrib.identity.models import (
    Identity,
    IdentityType
)

from knotis.contrib.relation.models import (
    Relation,
    RelationType
)


class RelationTestCase(unittest.TestCase):
    def setUp(self):
        self.individual = Identity.objects.create(
            name='Test Individual',
            description='Test Individual Description',
            identity_type=IdentityType.INDIVIDUAL
        )

        self.business = Identity.objects.create(
            name='Test Business',
            description='Test Business Description',
            identity_type=IdentityType.BUSINESS
        )

    def test_following(self):
        kwargs = {
            'owner': self.individual,
            'subject': self.business,
            'relation_type': RelationType.FOLLOWING
        }
        created = Relation.objects.create(**kwargs)

        selected = Relation.objects.get(pk=created.id)
        for key, value in kwargs.iteritems():
            self.assertEqual(value, getattr(selected, key))
