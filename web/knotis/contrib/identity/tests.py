from django.utils import unittest
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)


class IdentityTestCase(unittest.TestCase):
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

    def test_get_identity_images(self):
        self.assertTrue(False)
