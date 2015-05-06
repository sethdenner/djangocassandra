from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickIntegerField,
)


class PromoCodeTypes(object):
    UNDEFINED = -1
    OFFER_COLLECTION = 0
    RANDOM_OFFER_COLLECTION = 1
    CHOICES = (
        (OFFER_COLLECTION, 'Random Offer Collection'),
        (RANDOM_OFFER_COLLECTION, 'Offer Collection'),
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
            promo_code.value = str(promo_code.id)[:8]
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
