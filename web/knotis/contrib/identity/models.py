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


class IdentityIndividualManager(IdentityManager):
    def create(
        self,
        user,
        *args,
        **kwargs
    ):
        individual = super(IdentityIndividualManager, self).create(
            identity_type=IdentityTypes.INDIVIDUAL,
            name=user.full_name(),
            *args,
            **kwargs
        )

        Relation.objects.create_individual(
            user,
            individual
        )

        return individual

    def get_individual(
        self,
        user
    ):
        relation = Relation.objects.get_individual(
            user
        )
        return relation.related

    def get_query_set(self):
        return super(QuickManager, self).get_query_set().filter(
            identity_type=IdentityTypes.INDIVIDUAL
        )


class IdentityBusinessManager(IdentityManager):
    def create(
        self,
        manager,
        *args,
        **kwargs
    ):
        business = super(IdentityBusinessManager, self).create(
            identity_type=IdentityTypes.BUSINESS,
            *args,
            **kwargs
        )

        Relation.objects.create_manager(
            manager,
            business
        )

        return business

    def get_businesses(
        self,
        manager
    ):
        managed = Relation.objects.get_managed(manager)

        businesses = []
        for relation in managed:
            if relation.related.identity_type == IdentityTypes.BUSINESS:
                businesses.append(relation.related)

        return businesses

    def get_query_set(self):
        return super(QuickManager, self).get_query_set().filter(
            identity_type=IdentityTypes.BUSINESS
        )


class IdentityEstablishmentManager(IdentityManager):
    def create(
        self,
        business,
        *args,
        **kwargs
    ):
        establishment = super(IdentityEstablishmentManager, self).create(
            identity_type=IdentityTypes.ESTABLISHMENT,
            *args,
            **kwargs
        )

        Relation.objects.create_establishment(
            business,
            establishment
        )

        return establishment

    def get_establishments(
        self,
        identity
    ):
        if identity.identity_type == IdentityTypes.INDIVIDUAL:
            relations = Relation.objects.get_managed(identity)

        elif identity.identity_type == IdentityTypes.BUSINESS:
            relations = Relation.objects.get_establishments(identity)

        else:
            raise Exception(
                'can only get establishments by manager or by business'
            )

        establishments = []
        for relation in relations:
            if not hasattr(relation.related, 'identity_type'):
                continue

            if relation.related.identity_type == IdentityTypes.BUSINESS:
                establishments += self.get_establishments(relation.related)

            elif relation.related.identity_type == IdentityTypes.ESTABLISHMENT:
                establishments.append(relation.related)

            else:
                continue

        return establishments

    def get_query_set(self):
        return super(QuickManager, self).get_query_set().filter(
            identity_type=IdentityTypes.ESTABLISHMENT
        )


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
