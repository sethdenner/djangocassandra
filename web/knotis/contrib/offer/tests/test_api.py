
from unittest import TestCase

from .utils import OfferTestUtils
from knotis.contrib.offer.models import (
    OfferTypes
)


class OfferTests(TestCase):
    def test_create_dark(self):
        offer = OfferTestUtils.create_test_offer(offer_type=OfferTypes.DARK)
        self.assertIsNotNone(offer)
