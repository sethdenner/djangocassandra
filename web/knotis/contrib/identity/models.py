from django.utils.translation import ugettext_lazy as _

from knotis.contrib.quick.models import QuickModel
from knotis.contrib.quick.fields import (
    QuickForeignKey,
    QuickCharField,
    QuickTextField,
    QuickIntegerField
)

from knotis.contrib.media.models import Image

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
    primary_image = QuickForeignKey(Image)

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

    class Meta:
        proxy = True

    def clean(self):
        print ("Cleaning IdentityIndividual")
        self.identity_type = IdentityTypes.INDIVIDUAL


class IdentityBusiness(Identity):
    class Quick(Identity.Quick):
        exclude = ('identity_type',)
        filters = {'identity_type': IdentityTypes.BUSINESS}
        name = 'business'

    views = Identity.Quick.views
    views.update({
        'detail_customized': 'identitybusiness/DetailView.html',
        'detail': 'identitybusiness/DetailView.html'
    })

    class Meta:
        proxy = True

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

    def clean(self):
        print ("Cleaning IdentityEstablishment")
        self.identity_type = IdentityTypes.ESTABLISHMENT
