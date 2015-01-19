from unittest import TestCase

from .utils import TransactionTestUtils


class TestBookProvision(TestCase):
    def setUp(self):
        self.transaction_collection = \
            TransactionTestUtils.create_test_transaction_collection()

    def test_is_not_none(self):
        self.assertIsNotNone(self.transaction_collection)
