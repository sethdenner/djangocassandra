import urllib

from django.core.files import File
from django.test import TestCase
from django.contrib.auth import authenticate
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.contenttypes.models import ContentType

from knotis.contrib.media.models import Image
from knotis.contrib.auth.models import (
    KnotisUser,
    UserInformation
)
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)
from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)


class AuthenticationBackendTests(TestCase):
    def test_endpoint_validation(self):
        try:
            # Create a test user.
            username = 'test_user@knotis.com'
            user, _ = KnotisUser.objects.create_user(
                'First Name',
                'Last Name',
                username,
                'test_password'
            )

            # Create endpoint.
            endpoint = Endpoint.objects.create_endpoint(
                EndpointTypes.EMAIL,
                username,
                user,
                True
            )

            # Attempt authentication.
            authenticated_user = authenticate(
                user_id=user.id,
                validation_key=endpoint.validation_key
            )

            self.assertNotEqual(
                authenticated_user,
                None,
                'Authentication Failed'
            )

            validated_endpoint = Endpoint.objects.get(pk=endpoint.id)

            self.assertEqual(
                validated_endpoint.validated,
                True,
                'Endpoint Was Not Validated'
            )

            # Make sure the same credentials don't auth again.
            authenticated_user = authenticate(
                user_id=user.id,
                validation_key=endpoint.validation_key
            )

            self.assertEqual(
                authenticated_user,
                None,
                'Validation Credentials Did Not Expire.'
            )

        except:
            logger.exception()
            user = None

        finally:
            #clean up after ourselves.
            if user:
                try:
                    endpoints = Endpoint.objects.filter(user=user)
                    for endpoint in endpoints:
                        endpoint.delete()

                except:
                    pass

                user.delete()


class UserCreationTests(TestCase):
    def test_create_user(self):
        username = 'test_user@example.com'
        user, identity = KnotisUser.objects.create_user(
            'First Name',
            'Last Name',
            username,
            'test_password'
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
        self.user, self.identity = KnotisUser.objects.create_user(
            'First Name',
            'Last Name',
            'first.last@example.com',
            'test_password'
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
