from django.test import TestCase
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.contenttypes.models import ContentType

from knotis.contrib.auth.models import (
    UserInformation
)
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)
from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)

from .utils import UserCreationTestUtils

import random


class UserCreationTests(TestCase):

    def setUp(self):
        self.username = 'test+' + str(random.randint(0, 1000)) + '@knotis.com'

        self.user, self.identity = UserCreationTestUtils.create_test_user(
            email=self.username
        )

    def test_user_info(self):
        self.assertEqual(self.username, self.user.username)

    def test_userinformation(self):
        user_information = UserInformation.objects.get(user=self.user)
        self.assertIsNotNone(user_information)

    def test_default_identity_name(self):
        user_information = UserInformation.objects.get(user=self.user)
        self.assertEqual(
            self.identity.name,
            user_information.default_identity.name
        )

    def test_default_identity(self):
        user_information = UserInformation.objects.get(user=self.user)
        self.assertEqual(
            self.identity.id,
            user_information.default_identity.id
        )

    # Commenting this because I want to get it working but not now.
    # def test_primary_image(self):
    #     result = urllib.urlretrieve('http://placehold.it/1x1')

    #     image = Image.objects.create(
    #         owner=self.identity,
    #         image=File(open(result[0])),
    #     )

    #     self.identity_primary_image = ImageInstance.objects.create(
    #         owner=self.identity,
    #         image=image,
    #         related_object_id=self.identity.id
    #     )

    #     self.identity.primary_image = self.identity_primary_image
    #     self.identity.save()
    #     user_information = UserInformation.objects.get(user=self.user)
    #     user_information.default_identity_image = self.identity_primary_image

    #     self.assertEqual(
    #         self.identity.primary_image.image.url,
    #         user_information.default_identity_image.url
    #     )

    def test_relations(self):
        user_type = ContentType.objects.get_for_model(self.user)
        relations = Relation.objects.filter(
            subject_content_type__pk=user_type.id,
            subject_object_id=self.user.id
        )

        self.assertEqual(1, relations.count())

        relation = relations[0]

        self.assertEqual(relation.relation_type, RelationTypes.INDIVIDUAL)
        self.assertTrue(isinstance(relation.related, Identity))
        self.assertEqual(
            relation.related.identity_type,
            IdentityTypes.INDIVIDUAL
        )
