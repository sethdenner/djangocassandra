from unittest import TestCase
from knotis.contrib.auth.tests.utils import UserCreationTestUtils

from knotis.contrib.promocode.models import (
    PromoCode,
    PromoCodeTypes,
    ConnectPromoCode,
    AlreadyUsedException
)

from knotis.contrib.activity.models import (
    Activity,
)


class PromoCodeTests(TestCase):
    def setUp(self):
        self.promo_code = PromoCode.objects.create()

    def test_promo_code_id(self):
        self.assertEqual(self.promo_code.value, self.promo_code.id[:8])


class PromoCodeConnectDuplicateTests(TestCase):
    def setUp(self):
        self.promo_code = ConnectPromoCode.objects.create(
            promo_code_type=PromoCodeTypes.OFFER_COLLECTION
        )
        self.knotis_user, self.identity = \
            UserCreationTestUtils.create_test_user()

        self.promo_code.execute(
            request=None,
            current_identity=self.identity
        )

        self.activities = Activity.objects.filter(
            context=self.promo_code.value
        )

    def test_activity(self):
        self.assertGreaterEqual(self.activities, 1)

    def test_no_duplicate(self):
        self.assertRaises(
            AlreadyUsedException,
            self.promo_code.execute,
            None, self.identity
        )

    def test_for_duplicates(self):
        _, identity = UserCreationTestUtils.create_test_user()
        self.promo_code.execute(
            request=None,
            current_identity=identity
        )
        self.assertGreaterEqual(
            Activity.objects.filter(
                context=self.promo_code.value
            ),
            2
        )
