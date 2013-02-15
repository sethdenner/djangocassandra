from django.utils import unittest
from django.contrib.contenttypes.models import ContentType

from knotis.contrib.auth.models import (
    KnotisUser
)

from knotis.contrib.identity.models import (
    Identity,
    IdentityBusiness,
    IdentityTypes
)

from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)


class IdentityTestCase(unittest.TestCase):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(IdentityTestCase, self).__init__(
            *args,
            **kwargs
        )

        self.user = None
        self.user_password = 'test_password'
        self.user_email = 'fake@example.com'

        self.business_name = 'Fake Business'

    def setUp(self):
        pass

    def test_identity_creation(self):
        identity_type = IdentityTypes.INDIVIDUAL
        name = 'Test Identity'
        description = 'Test Description'

        created = Identity.objects.create(
            identity_type=identity_type,
            name=name,
            description=description,
            primary_image=None
        )

        selected = Identity.objects.get(pk=created.id)
        self.assertEqual(selected.name, name)
        self.assertEqual(selected.description, description)
        self.assertEqual(selected.identity_type, identity_type)

    def test_business_creation(self):
        user, user_identity = KnotisUser.objects.create_user(
            'Test',
            'User',
            self.user_email,
            self.user_password
        )

        business = IdentityBusiness.objects.create(
            user_identity,
            name=self.business_name
        )

        relation_type = ContentType.objects.get_for_model(business)
        relations = Relation.objects.filter(
            related_content_type=relation_type,
            related_object_id=business.id
        )

        owner = None

        for relation in relations:
            if relation.relation_type == RelationTypes.OWNER:
                owner = relation
                break

        self.assertIsNotNone(owner)
        self.assertEqual(
            user_identity.id,
            owner.subject.id
        )

    def test_get_identity_images(self):
        self.assertTrue(False)
