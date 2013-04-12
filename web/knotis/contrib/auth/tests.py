import urllib

from django.core.files import File
from django.test import TestCase
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.contenttypes.models import ContentType

from knotis.contrib.media.models import Image
from knotis.contrib.auth.models import (
    KnotisUser,
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


class UserCreationTests(TestCase):
    @staticmethod
    def create_test_user(**kwargs):
        if not kwargs.get('first_name'):
            kwargs['first_name'] = 'Test'

        if not kwargs.get('last_name'):
            kwargs['last_name'] = 'User'

        if not kwargs.get('email'):
            kwargs['email'] = 'test_user@example.com'

        if not kwargs.get('password'):
            kwargs['password'] = 'test_password'

        return KnotisUser.objects.create_user(**kwargs)

    def test_create_user(self):
        username = 'test_user@example.com'
        user, identity = UserCreationTests.create_test_user(
            first_name='First Name',
            last_name='Last Name',
            email=username,
            password='test_password'
        )

        self.assertIsNotNone(user)
        self.assertIsNotNone(identity)

        result = urllib.urlretrieve('http://placehold.it/1x1')

        identity_primary_image = Image.objects.create_image(
            user,
            File(open(result[0])),
            related_object_id=identity.id
        )

        identity.primary_image = identity_primary_image
        identity.save()

        user_information = UserInformation.objects.get(pk=user.id)
        user_information.default_identity_image = identity_primary_image
        user_information.save()

        self.assertIsNotNone(user_information)
        self.assertEqual(username, user_information.username)
        self.assertEqual(identity.id, user_information.default_identity.id)
        self.assertEqual(
            identity.identity_type,
            user_information.default_identity_type
        )
        self.assertEqual(
            identity.name,
            user_information.default_identity_name
        )
        self.assertEqual(
            identity.primary_image.image.url,
            user_information.default_identity_image.url
        )

        user_type = ContentType.objects.get_for_model(user)
        relations = Relation.objects.filter(
            subject_content_type__pk=user_type.id,
            subject_object_id=user.id
        )

        self.assertEqual(1, relations.count())

        relation = relations[0]

        self.assertEqual(relation.relation_type, RelationTypes.OWNER)
        self.assertTrue(isinstance(relation.related, Identity))
        self.assertEqual(
            relation.related.identity_type,
            IdentityTypes.INDIVIDUAL
        )


class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.user, self.identity = UserCreationTests.create_test_user(
            first_name='First Name',
            last_name='Last Name',
            email='first.last@example.com',
            password='test_password'
        )

    def test_login(self):
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)

    def test_resend_validation_email(self):
        response = self.client.get(''.join([
            '/auth/resend_validation_email/',
            self.user.username,
            '/'
        ]))

        self.assertEqual(response.status_code, 200)
