from django.test import TestCase

from knotis.contrib.auth.tests import UserCreationTests
from knotis.contrib.identity.tests.utils import IdentityModelTestUtils
from knotis.contrib.product.tests import ProductTests
from knotis.contrib.offer.tests import OfferTests

from knotis.contrib.product.models import (
    Product,
    ProductTypes,
    CurrencyCodes
)
from knotis.contrib.inventory.models import Inventory

from models import (
    Transaction,
    TransactionTypes,
    TransactionItem
)


class TransactionTests(TestCase):
    def setUp(self):
        (
            self.consumer,
            self.consumer_identity
        ) = UserCreationTests.create_test_user(
            last_name='Consumer',
            email='test_consumer@example.com',
        )

        us_dollars = Product.currency.get(CurrencyCodes.USD)

        self.consumer_currency = Inventory.objects.create_stack_from_product(
            self.consumer_identity,
            us_dollars
        )
        self.consumer_currency.stock = 20.
        self.consumer_currency.save()

        (
            self.merchant,
            self.merchant_identity
        ) = UserCreationTests.create_test_user(
            last_name='Merchant',
            email='test_merchant@example.com',
        )

        self.business, self.establishment = \
            IdentityModelTestUtils.create_test_business(
                self.merchant_identity,
                name='Test Business'
            )

        self.establishment_currency = (
            Inventory.objects.create_stack_from_product(
                self.establishment,
                us_dollars
            )
        )

        self.product = ProductTests.create_test_product()

        self.establishment_inventory = (
            Inventory.objects.create_stack_from_product(
                self.establishment,
                self.product,
                20
            )
        )

        self.offer_inventory = Inventory.objects.split(
            self.establishment_inventory,
            self.establishment,
            5
        )

        self.establishment_offer = OfferTests.create_test_offer(
            owner=self.establishment,
            inventory=[self.offer_inventory]
        )

    def test_offer_purchase_and_cancel(self):
        def validate_transaction(
            transaction,
            transaction_type,
            offer,
            participants
        ):
            self.assertIsNotNone(transaction)
            self.assertEqual(
                transaction.transaction_type,
                transaction_type
            )

            def validate_participant(
                transaction,
                participants
            ):
                for participant in participants:
                    if transaction.owner_id == participant.id:
                        return participant

                return None

            participant = validate_participant(
                transaction,
                participants
            )

            self.assertIsNotNone(participant)
            self.assertEqual(
                transaction.offer_id,
                offer.id
            )

        def validate_transaction_item(
            product,
            stock,
            provider,
            recipient,
            items
        ):
            def find_item(
                product,
                items
            ):
                for item in items:
                    if item.inventory.product_id == product.id:
                        return item

                return None

            item = find_item(
                product,
                items
            )

            self.assertIsNotNone(item)
            self.assertEqual(
                item.inventory.stock,
                stock
            )
            self.assertEqual(
                item.inventory.provider_id,
                provider.id
            )
            self.assertEqual(
                item.inventory.recipient_id,
                recipient.id
            )

            return item

        offer_items = self.establishment_offer.offeritem_set.all()
        participants = [self.establishment, self.consumer_identity]

        quantity_to_purchase = 1
        purchases = Transaction.objects.create_purchase(
            self.establishment_offer,
            self.consumer_identity,
            quantity_to_purchase,
            self.consumer_currency
        )

        transaction_context = purchases[0].transaction_context

        for purchase in purchases:
            validate_transaction(
                purchase,
                TransactionTypes.PURCHASE,
                self.establishment_offer,
                participants
            )
            self.assertEqual(
                purchase.transaction_context,
                transaction_context
            )

            purchase_items = TransactionItem.objects.filter(
                transaction=purchase
            )
            self.assertEqual(
                (len(participants) - 1) + offer_items.count(),
                purchase_items.count()
            )
            validate_transaction_item(
                self.consumer_currency.product,
                self.establishment_offer.price_discount * quantity_to_purchase,
                self.consumer_identity,
                self.establishment,
                purchase_items
            )

            for item in offer_items:
                validate_transaction_item(
                    item.inventory.product,
                    item.inventory.stock,
                    self.establishment,
                    self.consumer_identity,
                    purchase_items
                )

        purchase_buyer = Transaction.objects.get(
            owner=self.consumer_identity,
            transaction_context=transaction_context,
            transaction_type=TransactionTypes.PURCHASE
        )
        purchase_items_buyer = TransactionItem.objects.filter(
            transaction=purchase_buyer
        )

        inventory_redeem = []
        for item in purchase_items_buyer:
            if item.inventory.recipient_id == self.consumer_identity.id:
                inventory_redeem.append(item.inventory)

        redemptions = Transaction.objects.create_redemption(
            self.establishment_offer,
            self.consumer_identity,
            inventory_redeem,
            transaction_context
        )

        purchase_items_buyer = TransactionItem.objects.filter(
            transaction=purchase_buyer
        )
        for redemption in redemptions:
            validate_transaction(
                purchase,
                TransactionTypes.PURCHASE,
                self.establishment_offer,
                participants
            )
            self.assertEqual(
                purchase.transaction_context,
                transaction_context
            )

            self.assertEqual(
                (len(participants) - 1) + offer_items.count(),
                purchase_items_buyer.count()
            )
            validate_transaction_item(
                self.consumer_currency.product,
                self.establishment_offer.price_discount * quantity_to_purchase,
                self.consumer_identity,
                self.establishment,
                purchase_items_buyer
            )

            for item in purchase_items_buyer:
                inventory = item.inventory
                if (
                    inventory.product.product_type == ProductTypes.CURRENCY
                ):
                    provider = self.consumer_identity
                    recipient = self.establishment

                else:
                    provider = self.establishment
                    recipient = self.consumer_identity

                validated_item = validate_transaction_item(
                    inventory.product,
                    inventory.stock,
                    provider,
                    recipient,
                    purchase_items_buyer
                )

                self.assertEqual(
                    True,
                    validated_item.inventory.deleted
                )

        cancelations = Transaction.objects.create_cancelation(
            self.establishment_offer,
            self.consumer_identity,
            transaction_context
        )

        purchased_inventory = Inventory.objects.get_stack(
            self.consumer_identity,
            offer_items[0].inventory.product
        )
        returned_inventory = Inventory.objects.split(
            purchased_inventory,
            self.establishment,
            3
        )

        returns = Transaction.objects.create_return(
            self.establishment_offer,
            self.consumer_identity,
            [returned_inventory],
            transaction_context
        )

        for returned in returns:
            return_items = TransactionItem.objects.filter(
                transaction=returned
            )

            validated_item = validate_transaction_item(
                returned_inventory.product,
                returned_inventory.stock,
                returned_inventory.provider,
                returned_inventory.recipient,
                return_items
            )

            self.assertEqual(
                True,
                validated_item.inventory.deleted
            )

        self.establishment_currency = Inventory.objects.get(
            pk=self.establishment_currency.id
        )
        refund_currency = Inventory.objects.split(
            self.establishment_currency,
            self.consumer_identity,
            5.
        )

        refunds = Transaction.objects.create_refund(
            self.establishment_offer,
            self.consumer_identity,
            [refund_currency],
            transaction_context
        )

        for refund in refunds:
            refund_items = TransactionItem.objects.filter(
                transaction=refund
            )

            validated_item = validate_transaction_item(
                refund_currency.product,
                refund_currency.stock,
                refund_currency.provider,
                refund_currency.recipient,
                refund_items
            )

            self.assertEqual(
                True,
                validated_item.inventory.deleted
            )
