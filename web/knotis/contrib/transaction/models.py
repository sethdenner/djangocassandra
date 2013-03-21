import uuid
import datetime
import itertools

from django.utils.log import logging
logger = logging.getLogger(__name__)
from knotis.utils.view import format_currency
from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickBooleanField,
    QuickForeignKey
)
from knotis.contrib.identity.models import Identity
from knotis.contrib.inventory.models import Inventory
from knotis.contrib.offer.models import (
    Offer,
    OfferItem
)
from knotis.contrib.product.models import (
    Product,
    ProductTypes,
    CurrencyCodes
)


class TransactionTypes:
    PURCHASE = 'purchase'
    PURCHASE_COMPLETED = 'purchase_completed'
    REDEMPTION = 'redemption'
    CANCELATION = 'cancelation'
    RETURN = 'return'
    REFUND = 'refund'
    TRANSFER = 'transfer'

    CHOICES = (
        (PURCHASE, 'Purchase'),
        (PURCHASE_COMPLETED, 'Purchase Completed'),
        (REDEMPTION, 'Redemption'),
        (CANCELATION, 'Cancelation'),
        (RETURN, 'Return'),
        (REFUND, 'Refund'),
        (TRANSFER, 'Transfer')
    )


class TransactionManager(QuickManager):
    def create_purchase(
        self,
        offer,
        buyer,
        currency,
        transaction_context=None
    ):
        # TODO: Figure out what transaction context should be...
        # Just a UUID or do we want to smuggle some data in here?
        if not transaction_context:
            transaction_context = uuid.uuid4().hex

        try:
            transaction_buyer = super(TransactionManager, self).create(
                owner=buyer,
                other=offer.owner,
                transaction_type=TransactionTypes.PURCHASE,
                offer=offer,
                transaction_context=transaction_context
            )
            transaction_seller = super(TransactionManager, self).create(
                owner=offer.owner,
                other=buyer,
                transaction_type=TransactionTypes.PURCHASE,
                offer=offer,
                transaction_context=transaction_context
            )

        except:
            logger.exception('failed to create transactions')
            raise

        currency, split_currency = Inventory.objects.split(
            currency,
            offer.owner,
            offer.price_discount
        )

        try:
            TransactionItem.objects.create(
                transaction_seller,
                split_currency
            )
            TransactionItem.objects.create(
                transaction_buyer,
                split_currency
            )

        except:
            logger.exception('Failed to create transaction items')
            raise

        return transaction_buyer, transaction_seller, split_currency

    def create_purchase_completed(
        self,
        offer,
        buyer,
        transaction_context
    ):
        try:
            transaction_buyer_purchase = Transaction.objects.get(
                owner=buyer,
                transaction_type=TransactionTypes.PURCHASE,
                offer=offer,
                transaction_context=transaction_context
            )

        except:
            logger.exception('failed to retrieve purchase transaction')
            raise

        try:
            transaction_buyer = super(TransactionManager, self).create(
                owner=buyer,
                other=offer.owner,
                transaction_type=TransactionTypes.PURCHASE_COMPLETED,
                offer=offer,
                transaction_context=transaction_context
            )
            transaction_seller = super(TransactionManager, self).create(
                owner=offer.owner,
                other=buyer,
                transaction_type=TransactionTypes.PURCHASE_COMPLETED,
                offer=offer,
                transaction_context=transaction_context
            )

        except:
            logger.exception('failed to create transactions')
            raise

        try:
            transaction_items = TransactionItem.objects.filter(
                transaction=transaction_buyer_purchase
            )

            for transaction_item in transaction_items:
                currency_buyer = transaction_item.inventory
                currency_seller_stack = Inventory.objects.get_recipient_stack(
                    currency_buyer
                )
                currency_seller_stack = Inventory.objects.stack(
                    currency_buyer,
                    currency_seller_stack
                )

        except:
            logger.exception('failed to stack purchase currency')
            raise

        try:
            inventory = []
            offer_items = OfferItem.objects.filter(offer=offer)
            for offer_item in offer_items:
                inventory_transaction = Inventory.objects.split(
                    offer_item.inventory,
                    buyer,
                    offer_item.stock
                )

                inventory.append(inventory_transaction)

                TransactionItem.objects.create(
                    transaction_seller,
                    inventory_transaction
                )
                TransactionItem.objects.create(
                    transaction_buyer,
                    inventory_transaction
                )

        except:
            logger.exception('failed to split inventory for transaction')
            raise

        return transaction_buyer, transaction_seller, inventory

    def create_redemption(
        self,
        offer,
        buyer,
        transaction_context
    ):
        try:
            transaction_buyer_purchase_completed = Transaction.objects.get(
                owner=buyer,
                transaction_type=TransactionTypes.PURCHASE_COMPLETED,
                offer=offer,
                transaction_context=transaction_context
            )

        except:
            logger.exception(
                'failed to retrieve purchase completed transaction'
            )
            raise

        try:
            transaction_buyer = super(TransactionManager, self).create(
                owner=buyer,
                other=offer.owner,
                transaction_type=TransactionTypes.REDEMPTION,
                offer=offer,
                transaction_context=transaction_context
            )
            transaction_seller = super(TransactionManager, self).create(
                owner=offer.owner,
                other=buyer,
                transaction_type=TransactionTypes.REDEMPTION,
                offer=offer,
                transaction_context=transaction_context
            )

        except:
            logger.exception('failed to create transactions')
            raise

        try:
            # if inventory is perishable don't bother creating
            # an inventory for the user. That inventory is no
            # longer tracked by our system.
            transaction_items = TransactionItem.objects.filter(
                transaction=transaction_buyer_purchase_completed
            )
            for transaction_item in transaction_items:
                inventory = transaction_item.inventory

                if not inventory.is_perishable():
                    buyer_stack = Inventory.objects.get_stack(
                        inventory.product,
                        buyer
                    )
                    buyer_stack = Inventory.objects.stack(
                        inventory,
                        buyer_stack
                    )

        except:
            logger.exception('failed to stack redemed inventory')
            raise

        return transaction_buyer, transaction_seller, buyer_stack

    def create_cancelation(
        self,
        offer,
        buyer,
        transaction_context
    ):
        try:
            transaction_buyer = super(TransactionManager, self).create(
                owner=buyer,
                other=offer.owner,
                transaction_type=TransactionTypes.CANCELATION,
                offer=offer,
                transaction_context=transaction_context
            )
            transaction_seller = super(TransactionManager, self).create(
                owner=offer.owner,
                other=buyer,
                transaction_type=TransactionTypes.CANCELATION,
                offer=offer,
                transaction_context=transaction_context
            )

        except:
            logger.exception('failed to create transactions')
            raise

        try:
            transactions_buyer_previous = Transaction.objects.filter(
                owner=buyer,
                offer=offer,
                transaction_context=transaction_context
            )

            for transaction in transactions_buyer_previous:
                transaction.revert()

        except:
            logger.exception('failed to revert transactions')
            raise

        return transaction_buyer, transaction_seller

    def create_return(
        self,
        buyer,
        inventory=[],
        refund=None,
        offer=None,
        transaction_context=None
    ):
        if offer and transaction_context:
            try:
                transaction_buyer_redemption = Transaction.objects.get(
                    owner=buyer,
                    other=offer.owner,
                    offer=offer,
                    transaction_context=transaction_context,
                    transaction_type=TransactionTypes.REDEMPTION
                )

            except:
                logger.exception('failed to get previous redemption')
                raise

        elif not transaction_context:
            transaction_buyer_redemption = None
            transaction_context = uuid.uuid4().hex

        try:
            if transaction_buyer_redemption:
                transaction_items = TransactionItem.objects.filter(
                    transaction_context=transaction_context
                )
                for transaction_item in transaction_items:
                    if (
                        transaction_item.inventory.product.product_type !=
                        ProductTypes.CURRENCY
                    ):
                        inventory.append(transaction_item.inventory)

        except:
            logger.exception('failed to get transaction items')
            raise

        if not inventory:
            raise Exception('could not determine inventory for return')

        try:
            transaction_buyer = super(TransactionManager, self).create(
                owner=buyer,
                other=offer.owner,
                transaction_type=TransactionTypes.RETURN,
                offer=offer,
                transaction_context=transaction_context
            )
            transaction_seller = super(TransactionManager, self).create(
                owner=offer.owner,
                other=buyer,
                transaction_type=TransactionTypes.RETURN,
                offer=offer,
                transaction_context=transaction_context
            )

        except:
            logger.exception('failed to create transactions')
            raise

        if offer and offer.end_date < datetime.datetime.utcnow():
            offer_items = OfferItem.objects.get(offer=offer)
            for i in inventory:
                for offer_item in offer_items:
                    if i.product_id == offer_item.inventory.product_id:
                        Inventory.objects.stack(
                            i,
                            offer_item.inventory
                        )
                        break

        else:
            for i in inventory:
                stack = Inventory.objects.get_stack(
                    i.product,
                    offer.owner
                )
                Inventory.objects.stack(
                    i,
                    stack
                )

        # Take some money off of the business stack and send it to the buyer
        currency_seller_stack = Inventory.objects.get_stack(
            Product.currency.get(CurrencyCodes.USD),
            offer.owner
        )
        currency_seller_stack, currency_buyer = Inventory.objects.split(
            currency_seller_stack,
            buyer,
            offer.price_discount
        )

        try:
            TransactionItem.objects.create(
                transaction_seller,
                split_currency
            )
            TransactionItem.objects.create(
                transaction_buyer,
                split_currency
            )

        except:
            logger.exception('Failed to create transaction items')
            raise

        return transaction_buyer, transaction_seller, split_currency

    def create_refund(
        self,
        offer,
        buyer
    ):
        pass

    def create(
        self,
        **kwargs
    ):
        create_methods = {}
        for transaction_type in TransactionTypes.CHOICES:
            create_methods[transaction_type] = 'create_' + transaction_type[0]

        return getattr(self, create_methods[transaction_type])(**kwargs)

    def get_daily_revenue(
        self,
        business
    ):
        purchases = self.filter(
            business=business,
            transaction_type=TransactionTypes.PURCHASE
        )

        daily_revenue = []
        day = 0
        while day < 7:
            daily_revenue.append(0.)
            day = day + 1

        for purchase in purchases:
            purchase_date = purchase.pub_date
            now = datetime.datetime.utcnow()
            if purchase_date < now - datetime.timedelta(weeks=1):
                continue

            day_index = purchase_date.weekday() + (6 - now.weekday())
            if day_index > 6:
                day_index = day_index - 6

            daily_revenue[day_index] = \
                daily_revenue[day_index] + purchase.value

        return daily_revenue

    def get_weekly_revenue(
        self,
        business
    ):
        purchases = self.filter(
            business=business,
            transaction_type=TransactionTypes.PURCHASE
        )

        now = datetime.datetime.utcnow()
        now_week = now.isocalendar()[1]
        start_week = now_week - 7

        def week(date):
            week = date.isocalendar()[1] - start_week
            return week

        purchase_values = [
            (purchase.pub_date, purchase.value) for purchase in purchases
        ]
        purchase_values.sort(key=lambda (date, value): date)

        weekly_revenue = []
        week_count = 0
        while week_count < 7:
            weekly_revenue.append(0.)
            week_count = week_count + 1

        for key, group in itertools.groupby(
            purchase_values,
            key=lambda (date, value): week(date)
        ):
            if key < 1:
                continue

            index = key - 1
            for item in group:
                weekly_revenue[index] = weekly_revenue[index] + item[1]

        return weekly_revenue

    def get_monthly_revenue(
        self,
        business
    ):
        purchases = self.filter(
            business=business,
            transaction_type=TransactionTypes.PURCHASE
        )

        monthly_revenue = []
        month = 0
        while month < 12:
            monthly_revenue.append(0.)
            month = month + 1

        for purchase in purchases:
            month = purchase.pub_date.month
            if month < 1 or month > 12:
                continue

            now = datetime.datetime.utcnow()
            month_index = month + (12 - now.month)
            if month_index > 12:
                month_index = month_index - 12

            month_index = month_index - 1

            monthly_revenue[month_index] = \
                monthly_revenue[month_index] + purchase.value

        return monthly_revenue


class Transaction(QuickModel):
    owner = QuickForeignKey(
        Identity,
        related_name='transaction_owner'
    )
    other = QuickForeignKey(
        Identity,
        related_name='transaction_other'
    )

    transaction_type = QuickCharField(
        max_length=64,
        null=True,
        choices=TransactionTypes.CHOICES,
        db_index=True
    )

    offer = QuickForeignKey(Offer)

    transaction_context = QuickCharField(
        max_length=1024,
        db_index=True
    )

    reverted = QuickBooleanField(default=False)

    objects = TransactionManager()

    def __unicode__(self):
        return '/'.join([
            self.user.username if self.user else 'None',
            self.business.business_name.value if self.business else 'None',
            self.offer.id if self.offer else 'None',
            unicode(self.transaction_type),
            self.transaction_context
        ])

    def revert(self):
        if self.reverted:
            return

        transaction_items = TransactionItem.objects.filter(
            transaction=self
        )

        for transaction_item in transaction_items:
            (
                provider_stack,
                recipient_stack
            ) = Inventory.objects.get_participating_stacks(
                transaction_item.inventory,
                offer=self.offer
            )

            provider_stack += transaction_item.inventory.stock
            recipient_stack  -= transaction_item.inventory.stock
            provider_stack.save()
            recipient_stack.save()

        self.reverted = True
        self.save()

        transaction_other = Transaction.objects.get(
            owner=self.other,
            other=self.owner,
            transaction_context=self.transaction_context,
            transaction_type=self.transaction_type
        )
        transaction_other.reverted = True
        transaction_other.save()

    def value_formatted(self):
        if 0 == self.quantity:
            return format_currency(0.)

        return format_currency(self.value / self.quantity)

    def purchases(self):
        try:
            purchases = Transaction.objects.filter(
                business=self.business,
                offer=self.offer,
                user=self.user,
                transaction_context=self.transaction_context,
                transaction_type=TransactionTypes.PURCHASE
            )
        except:
            purchases = None

        purchase_count = 0
        for purchase in purchases:
            purchase_count = purchase_count + purchase.quantity

        return purchase_count

    def redemptions(self):
        try:
            redemptions = Transaction.objects.filter(
                business=self.business,
                offer=self.offer,
                user=self.user,
                transaction_context=self.transaction_context,
                transaction_type=TransactionTypes.REDEMPTION
            )
        except:
            redemptions = None

        redemption_count = 0
        for redemption in redemptions:
            redemption_count = redemption_count + redemption.quantity

        return redemption_count

    def unredeemed(self):
        return self.purchases() - self.redemptions()

    def unredeemed_values(self):
        unredeemed = self.unredeemed()
        index = 0
        values = []
        while index < unredeemed:
            index = index + 1
            values.append(index)

        return values

    def redemption_code(self):
        if not self.offer:
            return None

        context_parts = self.transaction_context.split('|')
        if len(context_parts) != 3:
            return None

        return context_parts[2]


class TransactionItemManager(QuickManager):
    def create(
        self,
        transaction,
        inventory
    ):
        return super(TransactionItemManager, self).create(
            transaction=transaction,
            transaction_context=transaction.transaction_context,
            inventory=inventory
        )


class TransactionItem(QuickModel):
    transaction = QuickForeignKey(Transaction)
    transaction_context = QuickCharField(
        max_length=1024,
        db_index=True
    )

    inventory = QuickForeignKey(Inventory)

    objects = TransactionItemManager()
