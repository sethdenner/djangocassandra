import uuid
import datetime
import itertools

from django.utils.log import logging
from django.conf import settings
logger = logging.getLogger(__name__)
from knotis.utils.view import format_currency
from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickIntegerField,
    QuickBooleanField,
    QuickForeignKey
)
from knotis.contrib.identity.models import Identity
from knotis.contrib.inventory.models import Inventory
from knotis.contrib.product.models import ProductTypes
from knotis.contrib.offer.models import (
    Offer,
    OfferItem
)


class TransactionTypes:
    PURCHASE = 'purchase'
    REDEMPTION = 'redemption'
    CANCELATION = 'cancelation'
    RETURN = 'return'
    REFUND = 'refund'
    TRANSFER = 'transfer'
    TRANSACTION_TRANSFER = 'transaction_transfer'
    DARK_PURCHASE = 'dark_purchase'

    CHOICES = (
        (PURCHASE, 'Purchase'),
        (REDEMPTION, 'Redemption'),
        (CANCELATION, 'Cancelation'),
        (RETURN, 'Return'),
        (REFUND, 'Refund'),
        (TRANSFER, 'Transfer'),
        (TRANSACTION_TRANSFER, 'Transaction Transfer'),
        (DARK_PURCHASE, 'Dark Purchase'),
    )


class TransactionManager(QuickManager):
    def create_purchase(
        self,
        offer,
        buyer,
        currency,
        transaction_context=None,
        force_free=False,
        dark_purchase=False
    ):
        if not offer.available():
            raise Exception(
                'Could not purchase offer {%s}. Offer is not available' % (
                    offer.id,
                )
            )

        # TODO: Figure out what transaction context should be...
        # Just a UUID or do we want to smuggle some data in here?
        if not transaction_context:
            transaction_context = uuid.uuid4().hex

        try:
            currency_seller_stack = Inventory.objects.get_stack(
                offer.owner,
                currency.product,
                create_empty=True
            )
            if not currency_seller_stack:
                raise Exception('this seller does not accept this currency')

        except:
            logger.exception('failed to get seller currency')
            raise

        try:
            offer_items = OfferItem.objects.filter(
                offer=offer
            )

        except:
            logger.exception('failed to get offer items')
            raise

        participants = [offer.owner, buyer]

        def add_participant(
            participant,
            participants
        ):
            exists = False
            for p in participants:
                if p.id == participant.id:
                    exists = True
                    return

            if not exists:
                participants.append(participant)

        for item in offer_items:
            add_participant(
                item.inventory.provider,
                participants
            )

        try:
            transactions = []
            for participant in participants:
                transaction = super(TransactionManager, self).create(
                    owner=participant,
                    transaction_type=(
                        TransactionTypes.PURCHASE,
                        TransactionTypes.DARK_PURCHASE
                    )[dark_purchase],
                    offer=offer,
                    transaction_context=transaction_context
                )
                transactions.append(transaction)

        except:
            logger.exception('failed to create transactions')
            raise

        try:
            price = offer.price_discount()
            if price and not force_free:
                currency_owner = Inventory.objects.split(
                    currency,
                    offer.owner,
                    price
                )

            currencies_thrid_party = []
            for item in offer_items:
                if price and item.inventory.provider_id != offer.owner_id and not force_free:
                    split_currency = Inventory.objects.split(
                        currency_owner,
                        item.inventory.provider,
                        item.price_discount
                    )
                    currencies_thrid_party.append(split_currency)

                provider_stack = Inventory.objects.get_provider_stack(
                    item.inventory,
                    create_empty=True,
                )

                if (
                    not provider_stack.unlimited and
                    provider_stack.stock < item.inventory.stock
                ):
                    inventory = item.inventory

                else:
                    inventory = provider_stack

                inventory_transaction = Inventory.objects.split(
                    inventory,
                    buyer,
                    item.inventory.stock
                )

                for transaction in transactions:
                    TransactionItem.objects.create(
                        transaction,
                        inventory_transaction
                    )

            if price and not force_free:
                for transaction in transactions:
                    TransactionItem.objects.create(
                        transaction,
                        currency_owner
                    )
                    for c in currencies_thrid_party:
                        TransactionItem.objects.create(
                            transaction,
                            c
                        )

        except:
            logger.exception('failed to create transaction items')
            raise

        offer.purchase()
        return transactions

    def create_redemption(
        self,
        purchase
    ):
        if (
            not purchase
            or purchase.transaction_type != TransactionTypes.PURCHASE
        ):
            raise Exception('Cannot create redemption without purchase')

        try:
            purchase_items = TransactionItem.objects.filter(
                transaction=purchase
            )

            participants = []

            def add_participant(
                participant,
                participants
            ):
                exists = False
                for p in participants:
                    if p.id == participant.id:
                        exists = True
                        return

                if not exists:
                    participants.append(participant)

            inventory_redeem = []
            for item in purchase_items:
                inventory_redeem.append(item.inventory)
                add_participant(
                    item.inventory.provider,
                    participants
                )
                add_participant(
                    item.inventory.recipient,
                    participants
                )

        except Exception, e:
            logger.exception(e.message)
            raise

        try:
            transactions = []
            for participant in participants:
                transaction = super(TransactionManager, self).create(
                    owner=participant,
                    transaction_type=TransactionTypes.REDEMPTION,
                    offer=purchase.offer,
                    transaction_context=purchase.transaction_context
                )
                transactions.append(transaction)

        except:
            logger.exception('failed to create transactions')
            raise

        try:
            mode = purchase.mode()
            for i in inventory_redeem:
                recipient_stack = Inventory.objects.get_stack(
                    i.recipient,
                    i.product,
                    create_empty=True
                )

                if (
                    i.recipient == purchase.offer.owner and
                    i.product.product_type == ProductTypes.CURRENCY
                ):
                    if mode == 'stripe':
                        i.stock -= (
                            i.stock * (
                                settings.KNOTIS_MODE_PERCENT +
                                settings.STRIPE_MODE_PERCENT
                            ) + settings.STRIPE_MODE_FLAT
                        )
                        i.save()

                    elif mode == 'none':
                        i.stock -= (
                            i.stock * (
                                settings.KNOTIS_MODE_PERCENT
                            )
                        )
                        i.save()

                Inventory.objects.stack(
                    i,
                    recipient_stack
                )

        except:
            logger.exception('failed to stack inventory')
            raise

        return transactions

    def create_cancelation(
        self,
        offer,
        buyer,
        transaction_context
    ):
        try:
            transactions_buyer = self.filter(
                transaction_context=transaction_context
            )

        except:
            logger.exception('failed to get previous transactions')
            raise

        try:
            offer_items = OfferItem.objects.filter(
                offer=offer
            )

        except:
            logger.exception('failed to get offer items')
            raise

        try:
            def add_participant(
                participant,
                participants
            ):
                exists = False
                for p in participants:
                    if p.id == participant.id:
                        exists = True
                        return

                if not exists:
                    participants.append(participant)

            participants = [buyer, offer.owner]

            for item in offer_items:
                add_participant(
                    item.inventory.provider,
                    participants
                )
                add_participant(
                    item.inventory.recipient,
                    participants
                )

            transactions = []
            for participant in participants:
                transaction = super(TransactionManager, self).create(
                    owner=buyer,
                    transaction_type=TransactionTypes.CANCELATION,
                    offer=offer,
                    transaction_context=transaction_context
                )
                transactions.append(transaction)

        except:
            logger.exception('failed to create transactions')
            raise

        try:
            for transaction in transactions_buyer:
                transaction.revert()

        except:
            logger.exception('failed to revert tranactions')
            raise

        return transactions

    def _return_refund_refactor(
        self,
        offer,
        buyer,
        inventory,
        transaction_context,
        transaction_type
    ):
        try:
            purchase_buyer = Transaction.objects.get(
                owner=buyer,
                transaction_context=transaction_context,
                transaction_type=TransactionTypes.PURCHASE
            )

        except:
            logger.exception('failed to get purchase')
            raise

        try:
            Transaction.objects.get(
                owner=buyer,
                transaction_context=transaction_context,
                transaction_type=TransactionTypes.REDEMPTION
            )

        except:
            logger.exception('failed to get redemption')
            raise

        try:
            transaction_items = TransactionItem.objects.filter(
                transaction=purchase_buyer
            )

        except:
            logger.exception('failed to get transaction items')
            raise

        participants = [offer.owner, buyer]

        def add_participant(
            participant,
            participants
        ):
            exists = False
            for p in participants:
                if p.id == participant.id:
                    exists = True
                    return

            if not exists:
                participants.append(participant)

        inventory_cancelation = []
        for i in inventory:
            for item in transaction_items:
                if (
                    i.product_id == item.inventory.product_id and
                    i.recipient_id == item.inventory.provider_id and
                    i.stock <= item.inventory.stock
                ):
                    inventory_cancelation.append(i)
                    add_participant(
                        i.provider,
                        participants
                    )
                    add_participant(
                        item.inventory.recipient,
                        participants
                    )

        if len(inventory_cancelation) != len(inventory):
            raise Exception(
                ', '.join((
                    'The following inventories do not belong to this '
                    'transaction or they have already been returned'
                ), [
                    i.id for i in list(
                        set(inventory) - set(inventory_cancelation)
                    )
                ])
            )

        if not inventory_cancelation:
            raise Exception('could not determine inventory for return')

        try:
            transactions = []
            for participant in participants:
                transaction = super(TransactionManager, self).create(
                    owner=participant,
                    transaction_type=transaction_type,
                    offer=offer,
                    transaction_context=transaction_context
                )
                transactions.append(transaction)

        except:
            logger.exception('failed to create transactions')
            raise

        try:
            for i in inventory_cancelation:
                for transaction in transactions:
                    TransactionItem.objects.create(
                        transaction,
                        i
                    )

                stack = Inventory.objects.get_stack(
                    i.recipient,
                    i.product
                )
                Inventory.objects.stack(
                    i,
                    stack
                )

        except:
            logger.exception('failed to create transaction items')
            raise

        return transactions

    def create_return(
        self,
        offer,
        buyer,
        inventory,
        transaction_context
    ):
        return self._return_refund_refactor(
            offer,
            buyer,
            inventory,
            transaction_context,
            TransactionTypes.RETURN
        )

    def create_refund(
        self,
        offer,
        buyer,
        currency,
        transaction_context
    ):
        return self._return_refund_refactor(
            offer,
            buyer,
            currency,
            transaction_context,
            TransactionTypes.REFUND
        )

    def create_dark_purchase(
        self,
        offer,
        buyer,
        currency,
        transaction_context=None,
    ):
        return self.create_purchase(
            offer,
            buyer,
            currency,
            transaction_context,
            dark_purchase=True
        )

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
    owner = QuickForeignKey(Identity)
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

    def participants(self):
        transactions = Transaction.objects.filter(
            transaction_type=self.transaction_type,
            transaction_context=self.transaction_context
        )

        participants = []
        for t in transactions:
            participants.append(t.owner)

        return participants

    def revert(self):
        if self.reverted:
            return None

        transaction_items = TransactionItem.objects.filter(
            transaction=self
        )

        for transaction_item in transaction_items:
            (
                provider_stack,
                recipient_stack
            ) = Inventory.objects.get_participating_stacks(
                transaction_item.inventory
            )

            if not transaction_item.inventory.deleted:
                Inventory.objects.stack(
                    transaction_item.inventory,
                    provider_stack
                )

        self.reverted = True
        self.save()

        transaction_others = Transaction.objects.filter(
            transaction_context=self.transaction_context,
            transaction_type=self.transaction_type
        )

        for transaction in transaction_others:
            transaction.reverted = True
            transaction.save()

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
                offer=self.offer,
                transaction_context=self.transaction_context,
                transaction_type=TransactionTypes.REDEMPTION
            )
        except:
            redemptions = None

        return len(redemptions)

    def has_redemptions(self):
        return self.redemptions() != 0

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

    def mode(self):
        context_parts = self.transaction_context.split('|')
        if len(context_parts) < 4:
            return None

        return context_parts[3]

    def redemption_code(self):
        if not self.offer:
            return None

        context_parts = self.transaction_context.split('|')
        if len(context_parts) < 3:
            return None

        return context_parts[2]

    def quantity(self):
        purchases = Transaction.objects.filter(
            owner=self.owner,
            transaction_type=TransactionTypes.PURCHASE,
            transaction_context=self.transaction_context
        )

        return len(purchases)


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


class TransactionCollection(QuickModel):
    objects = QuickManager()
    neighborhood = QuickCharField(max_length=255, db_index=True)


class TransactionCollectionItem(QuickModel):
    transaction_collection = QuickForeignKey(TransactionCollection)
    transaction = QuickForeignKey(Transaction)
    page = QuickIntegerField(db_index=True)
    objects = QuickManager()
