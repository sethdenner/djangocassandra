from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from knotis.contrib.auth.models import (
    KnotisUser
)

from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)

from models import (
    Identity,
    IdentityTypes,
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
    def create_test_business(**kwargs):
        if not kwargs.get('name'):
            kwargs['name'] = 'Test Business'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Business description.'

        return IdentityBusiness.objects.create(**kwargs)

    @staticmethod
    def create_test_establishment(**kwargs):
        if not kwargs.get('name'):
            kwargs['name'] = 'Test Establishment'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Establishment description.'

        return IdentityEstablishment.objects.create(**kwargs)

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(IdentityModelTests, self).__init__(
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


class IdentityViewTests(TestCase):
    def setUp(self):
        self.user_email = 'test@example.com'
        self.user_password = 'test_password'
        self.user, self.user_identity = KnotisUser.objects.create_user(
            'Test',
            'User',
            self.user_email,
            self.user_password
        )

    def test_identity_switcher_view(self):
        self.client.login(
            username=self.user_email,
            password=self.user_password
        )
        response = self.client.get('/identity/switcher/')
        self.assertEqual(response.status_code, 200)

    def test_identity_switcher_fragment(self):
        pass
