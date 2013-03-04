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
    OWNER = 'owner'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'
    FOLLOWING = 'following'
    LIKES = 'likes'
    CUSTOMER = 'customer'
    CONTRIBUTOR = 'contributor'

    CHOICES = (
        (UNDEFINED, 'Undefined'),
        (OWNER, 'Owner'),
        (MANAGER, 'Manager'),
        (EMPLOYEE, 'Employee'),
        (FOLLOWING, 'Following'),
        (LIKES, 'Likes'),
        (CUSTOMER, 'Customer')
    )


class RelationManager(QuickManager):
    pass


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
    name = QuickCharField(
        max_length=80,
        db_index=True,
        required=True
    )
    description = QuickTextField(
        required=True
    )

    objects = RelationManager()

    class Quick(QuickModel.Quick):
        exclude = ()
        # permissions = {'create': self.check_create}
        types = RelationTypes

    def __unicode__(self):
        if (self.name):
            return str(self.name)
        return str(self.id)


class RelationOwner(Relation):
    class Quick(Relation.Quick):
        exclude = ('relation_type',)
        filters = {'relation_type': RelationTypes.OWNER}

    class Meta:
        proxy = True

    def clean(self):
        self.relation_type = RelationTypes.OWNER


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
