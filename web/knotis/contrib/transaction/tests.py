from django.test import TestCase

from models import Transaction


class TransactionTests(TestCase):
    def test_create(self):
        transaction = Transaction.objects.create_transaction()
        self.assertIsNotNone(transaction)
