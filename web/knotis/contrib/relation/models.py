from django.contrib.contenttypes.models import ContentType

from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickTextField,
    QuickForeignKey,
    QuickUUIDField,
    QuickGenericForeignKey
)

__models__ = (
    'Relation',
    'RelationOwner',
    'RelationManager',
    'RelationEmployee'
)
__all__ = __models__ + ('RelationTypes',)


class RelationTypes:
    """
    There should be a good way to map type number to the actual type.
    There should be a way to specify the class.
    Types could be inferred from the models list.
    """
    UNDEFINED = 'undefined'
    INDIVIDUAL = 'individual'
    PROPRIETOR = 'proprietor'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'
    ESTABLISHMENT = 'establishment'
    FOLLOWING = 'following'
    LIKES = 'likes'
    CUSTOMER = 'customer'
    CONTRIBUTOR = 'contributor'

    CHOICES = (
        (UNDEFINED, 'Undefined'),
        (INDIVIDUAL, 'Individual'),
        (PROPRIETOR, 'Proprietor'),
        (MANAGER, 'Manager'),
        (EMPLOYEE, 'Employee'),
        (ESTABLISHMENT, 'Establishment'),
        (FOLLOWING, 'Following'),
        (LIKES, 'Likes'),
        (CUSTOMER, 'Customer')
    )


class RelationManager(QuickManager):
    def create_individual(
        self,
        user,
        individual
    ):
        return self.create(
            relation_type=RelationTypes.INDIVIDUAL,
            subject=user,
            related=individual,
            description=''.join([
                'The identity of ',
                individual.name,
                '.'
            ])
        )

    def get_individual(
        self,
        user
    ):
        user_type = ContentType.objects.get_for_model(user)
        return Relation.objects.get(
            subject_content_type__pk=user_type.id,
            subject_object_id=user.id
        )

    def create_manager(
        self,
        manager,
        related
    ):
        return self.create(
            relation_type=RelationTypes.MANAGER,
            subject=manager,
            related=related,
            description=''.join([
                manager.name,
                ' is a manager of ',
                related.name
            ])
        )

    def get_managers(
        self,
        related
    ):
        related_type = ContentType.objects.get_for_model(related)
        return self.filter(
            related_content_type__pk=related_type.id,
            related_object_id=related.id,
            relation_type=RelationTypes.MANAGER
        )

    def get_managed(
        self,
        manager
    ):
        manager_type = ContentType.objects.get_for_model(manager)
        return self.filter(
            subject_content_type__pk=manager_type.id,
            subject_object_id=manager.id,
            relation_type=RelationTypes.MANAGER
        )

    def create_establishment(
        self,
        business,
        establishment
    ):
        return self.create(
            relation_type=RelationTypes.ESTABLISHMENT,
            subject=business,
            related=establishment,
            description=''.join([
                establishment.name,
                ' is a establishment of ',
                business.name
            ])
        )

    def get_establishments(
        self,
        business
    ):
        business_type = ContentType.objects.get_for_model(business)
        return self.filter(
            subject_content_type__pk=business_type.id,
            subject_object_id=business.id,
            relation_type=RelationTypes.ESTABLISHMENT
        )

    def create_following(
        self,
        follower,
        related
    ):
        return self.create(
            relation_type=RelationTypes.FOLLOWING,
            subject=follower,
            related=related,
            description=''.join([
                follower.name,
                ' is following ',
                related.name
            ])
        )

    def get_following(
        self,
        follower
    ):
        follower_type = ContentType.objects.get_for_model(follower)
        return self.filter(
            subject_content_type__pk=follower_type.id,
            subject_object_id=follower.id,
            relation_type=RelationTypes.FOLLOWING
        )


class Relation(QuickModel):
    relation_type = QuickCharField(
        choices=RelationTypes.CHOICES,
        default=RelationTypes.UNDEFINED,
        max_length=25,
    )
    subject_content_type = QuickForeignKey(
        ContentType,
        related_name='relation_subject_set'
    )
    subject_object_id = QuickUUIDField()
    subject = QuickGenericForeignKey(
        'subject_content_type',
        'subject_object_id'
    )
    related_content_type = QuickForeignKey(
        ContentType,
        related_name='relation_related_set'
    )
    related_object_id = QuickUUIDField()
    related = QuickGenericForeignKey(
        'related_content_type',
        'related_object_id'
    )
    description = QuickTextField(
        required=True
    )

    objects = RelationManager()


class RelationProprietor(Relation):
    class Quick(Relation.Quick):
        exclude = ('relation_type',)
        filters = {'relation_type': RelationTypes.PROPRIETOR}

    class Meta:
        proxy = True

    def clean(self):
        self.relation_type = RelationTypes.PROPRIETOR


class RelationFollowing(Relation):
    class Meta:
        proxy = True

    class Quick(Relation.Quick):
        exclude = ('relation_type',)
        filters = {'relation_type': RelationTypes.FOLLOWING}

    def clean(self):
        print ("premium clean")
        self.relation_type = RelationTypes.FOLLOWING


class RelationEmployee(Relation):
    class Meta:
        proxy = True

    class Quick(Relation.Quick):
        exclude = ('relation_type',)
        filters = {'relation_type': RelationTypes.EMPLOYEE}

    def clean(self):
        self.relation_type = RelationTypes.EMPLOYEE
