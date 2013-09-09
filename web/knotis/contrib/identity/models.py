import re

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.utils.http import urlquote

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
            subject_content_type=identity_content_type,
            subject_object_id=user_identity.id,
            related_content_type=identity_content_type
        )
        for relation in identity_relations:
            identities.add(relation.related)

        return identities

    def get_managed(
        self,
        identity
    ):
        managed_relations = Relation.objects.get_managed(identity)
        managed_ids = []
        for relation in managed_relations:
            managed_ids.append(relation.related_object_id)

        return Identity.objects.filter(id__in=managed_ids)


class IdentityIndividualManager(IdentityManager):
    def create(
        self,
        user,
        *args,
        **kwargs
    ):
        name = kwargs.get('name', IdentityIndividual.DEFAULT_NAME)

        individual = super(IdentityIndividualManager, self).create(
            identity_type=IdentityTypes.INDIVIDUAL,
            name=name,
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

        return self.get(pk=relation.related_object_id)

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

    def get_establishment_parent(
        self,
        establishment
    ):
        business = None

        relation_establishment = Relation.objects.get(
            relation_type=RelationTypes.ESTABLISHMENT,
            related_object_id=establishment.id
        )

        business = relation_establishment.subject
        return business

    def get_query_set(self):
        return super(QuickManager, self).get_query_set().filter(
            identity_type=IdentityTypes.BUSINESS
        )


class IdentityEstablishmentManager(IdentityManager):
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
    class Quick(QuickModel.Quick):
        exclude = ()
        pass

    DEFAULT_NAME = 'New Identity'

    identity_type = QuickIntegerField(
        choices=IdentityTypes.CHOICES,
        default=IdentityTypes.UNDEFINED,
        blank=False
    )
    name = QuickCharField(
        max_length=80,
        verbose_name=_('Identity Name'),
        blank=False
    )
    backend_name = QuickCharField(
        max_length=80,
        db_index=True,
        verbose_name=_('Backend Name')
    )
    description = QuickTextField(
        verbose_name=_('Describe the Identity')
    )
    primary_image = QuickForeignKey('media.Image')

    objects = IdentityManager()

    def is_name_default(self):
        return self.DEFAULT_NAME == self.name

    def is_manager(
        self,
        identity
    ):
        """
        Returns True is self is manager of identity.
        """
        managed_relations = Relation.objects.get_managed(self)
        for rel in managed_relations:
            if rel.related_object_id == identity.pk:
                return True

        return False

    @staticmethod
    def _clean_backend_name(name):
        backend_name = name.replace(
            '&',
            'and'
        ).replace(
            '/',
            '-'
        )

        backend_name = urlquote(
            backend_name.strip().lower().replace(
                ' ',
                '-'
            )
        )
        backend_name = re.sub(
            r'%[0-9a-fA-F]{2}',
            '',
            backend_name
        )

        return backend_name

    def clean(self):
        pass

    def __unicode__(self):
        if (self.name):
            return str(self.name)
        return str(self.id)


class IdentityIndividual(Identity):
    DEFAULT_NAME = 'New User'

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
        return super(IdentityIndividual, self).clean()


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

        if self.name and not self.backend_name:
            self.backend_name = self._clean_backend_name(self.name)

        return super(IdentityBusiness, self).clean()


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

        if self.name and not self.backend_name:
            self.backend_name = self._clean_backend_name(self.name)

        return super(IdentityEstablishment, self).clean()
