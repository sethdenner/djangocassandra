from django.utils import unittest

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)

from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)


class RelationTestCase(unittest.TestCase):
    def setUp(self):
        self.individual = Identity.objects.create(
            name='Test Individual',
            description='Test Individual Description',
            identity_type=IdentityTypes.INDIVIDUAL
        )

        self.business = Identity.objects.create(
            name='Test Business',
            description='Test Business Description',
            identity_type=IdentityTypes.BUSINESS
        )

    def test_following(self):
        kwargs = {
            'owner': self.individual,
            'subject': self.business,
            'relation_type': RelationTypes.FOLLOWING
        }
        created = Relation.objects.create(**kwargs)

        #import pdb
        #pdb.set_trace()

        selected = Relation.objects.get(pk=created.id)
        for key, value in kwargs.iteritems():
            self.assertEqual(value, getattr(selected, key))
