from unittest import TestCase

from knotis.contrib.promocode.models import (
    PromoCode,
)


class PromoCodeTests(TestCase):
    def setUp(self):
        self.promo_code = PromoCode.objects.create()

    def test_promo_code_id(self):
        self.assertEqual(self.promo_code.value, self.promo_code.id[:8])
