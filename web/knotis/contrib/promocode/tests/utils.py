

from knotis.contrib.promocode.models import (
    PromoCode,
    PromoCodeTypes,
)


class PromoCodeTestUtils(object):
    @staticmethod
    def create_collection_promo_code(**kwargs):
        if not kwargs.get('promo_code_type'):
            kwargs['promo_code_type'] = PromoCodeTypes.OFFER_COLLECTION

        return PromoCode.objects.create(
            kwargs
        )
