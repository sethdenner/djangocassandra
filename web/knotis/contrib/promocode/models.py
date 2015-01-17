from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickIntegerField,
)
from knotis.contrib.activity.models import (
    Activity,
    ActivityTypes
)


class PromoCodeTypes(object):
    UNDEFINED = -1
    OFFER_COLLECTION = 0
    CHOICES = (
        (OFFER_COLLECTION, 'Offer Collection'),
        (UNDEFINED, 'Undefined'),
    )


class PromoCodeManager(QuickManager):
    def create(
        self,
        *args,
        **kwargs
    ):
        promo_code = super(PromoCodeManager, self).create(
            *args,
            **kwargs
        )
        if kwargs.get('value', None) is None:
            promo_code.value = promo_code.id[:8]
            promo_code.save()
        return promo_code


class PromoCode(QuickModel):
    '''
    Meant to query the activity table to tell if the same user attempts to
    use the same promocode twice.
    '''
    promo_code_type = QuickIntegerField(
        choices=PromoCodeTypes.CHOICES,
        default=PromoCodeTypes.UNDEFINED,
        blank=False
    )
    value = QuickCharField(
        null=True,
        default=None,
        max_length=64,
    )
    context = QuickCharField(
        null=True,
        default=None,
        max_length=1024
    )

    objects = PromoCodeManager()

    def execute(self, request=None, current_identity=None):
        raise NotImplemented(
            'This needs to be implemented for derived classes.'
        )


class ConnectPromoCode(PromoCode):

    class Meta:
        proxy = True

    def execute(
        self,
        current_identity
    ):
        Activity.objects.create(
            identity=current_identity,
            context=self.value,
            activity_type=ActivityTypes.PROMO_CODE
        )
