from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickForeignKey,
    QuickCharField,
    QuickTextField,
    QuickIntegerField
)

from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)

__models__ = (
    'Identity',
    'IdentityIndividual',
    'IdentityBusiness',
    'IdentityEstablishment'
)
__all__ = __models__ + ('IdentityTypes',)


class IdentityTypes:
    UNDEFINED = -1
    INDIVIDUAL = 0
    BUSINESS = 1
    ESTABLISHMENT = 2

    CHOICES = (
        (UNDEFINED, 'Undefined'),
        (INDIVIDUAL, 'Individual'),
        (BUSINESS, 'Business'),
        (ESTABLISHMENT, 'Establishment'),
    )


class IdentityManager(QuickManager):
    def create(
        self,
        owner=None,
        *args,
        **kwargs
    ):
        identity = super(IdentityManager, self).create(
            *args,
            **kwargs
        )

        if owner:
            relation_type = RelationTypes.OWNER

            Relation.objects.create(
                subject=owner,
                related=identity,
                relation_type=relation_type
            )

        return identity

    def get_individual(
        self,
        user
    ):
        user_type = ContentType.objects.get_for_model(user)
        relation = Relation.objects.get(
            subject_content_type__pk=user_type.id,
            subject_object_id=user.id
        )
        return relation.related

    def get_available(
        self,
        user
    ):
        identities = set()

        user_content_type = ContentType.objects.get_for_model(user)
        user_identity_relation = Relation.objects.get(
            subject_content_type__pk=user_content_type.id,
            subject_object_id=user.id
        )
        user_identity = user_identity_relation.related
        identities.add(user_identity)

        identity_content_type = ContentType.objects.get_for_model(
            user_identity
        )
        identity_relations = Relation.objects.filter(
            relation_type=RelationTypes.MANAGER,
            subject_content_type__pk=identity_content_type.id,
            subject_object_id=user_identity.id,
            related_content_type=identity_content_type.id
        )
        for relation in identity_relations:
            identities.add(relation.related)

        return identities


class Identity(QuickModel):
    identity_type = QuickIntegerField(
        choices=IdentityTypes.CHOICES,
        default=IdentityTypes.UNDEFINED
    )
    name = QuickCharField(
        max_length=80,
        db_index=True,
        verbose_name=_("Identity Name"),
        required=True
    )
    description = QuickTextField(
        verbose_name=_("Describe the Identity"),
        required=True
    )
    primary_image = QuickForeignKey('media.Image')

    objects = IdentityManager()

    class Quick(QuickModel.Quick):
        exclude = ()
        pass

    def __unicode__(self):
        if (self.name):
            return str(self.name)
        return str(self.id)


class IdentityIndividualManager(IdentityManager):
    def create(
        self,
        *args,
        **kwargs
    ):
        kwargs['identity_type'] = IdentityTypes.INDIVIDUAL
        return super(IdentityIndividualManager, self).create(
            *args,
            **kwargs
        )


class IdentityIndividual(Identity):
    class Quick(Identity.Quick):
        exclude = ('identity_type',)
        filters = {'identity_type': IdentityTypes.INDIVIDUAL}
        name = 'individual'
        field_overrides = {'name': {'verbose_name': _('User Name')}}

    class Meta:
        proxy = True

    objects = IdentityIndividualManager()

    def clean(self):
        print ("Cleaning IdentityIndividual")
        self.identity_type = IdentityTypes.INDIVIDUAL


class IdentityBusinessManager(IdentityManager):
    def create(
        self,
        *args,
        **kwargs
    ):
        kwargs['identity_type'] = IdentityTypes.BUSINESS
        return super(IdentityBusinessManager, self).create(
            *args,
            **kwargs
        )


class IdentityBusiness(Identity):
    class Meta:
        proxy = True

    class Quick(Identity.Quick):
        exclude = ('identity_type',)
        filters = {'identity_type': IdentityTypes.BUSINESS}
        name = 'business'

    views = Identity.Quick.views
    views.update({
        'detail_customized': 'identitybusiness/DetailView.html',
        'detail': 'identitybusiness/DetailView.html'
    })

    objects = IdentityBusinessManager()

    def clean(self):
        print ("Cleaning IdentityBusiness")
        self.identity_type = IdentityTypes.BUSINESS


class IdentityEstablishmentManager(IdentityManager):
    def create(
        self,
        *args,
        **kwargs
    ):
        kwargs['identity_type'] = IdentityTypes.ESTABLISHMENT
        return super(IdentityEstablishmentManager, self).create(
            *args,
            **kwargs
        )


class IdentityEstablishment(Identity):
    class Quick(Identity.Quick):
        exclude = ('identity_type',)
        filters = {'identity_type': IdentityTypes.ESTABLISHMENT}
        name = 'establishment'

    class Meta:
        proxy = True

    objects = IdentityEstablishmentManager()

    def clean(self):
        print ("Cleaning IdentityEstablishment")
        self.identity_type = IdentityTypes.ESTABLISHMENT
