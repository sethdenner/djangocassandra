import datetime
import itertools

from knotis.utils.view import format_currency
from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickFloatField,
    QuickForeignKey
)
from knotis.contrib.identity.models import Identity
from knotis.contirb.inventory.models import Inventory
from knotis.contrib.offer.models import Offer


class TransactionTypes:
    PURCHASE = 'purchase'
    PURCHASE_COMPLETED = 'purchase_completed'
    SALE = 'sale'
    SALE_PENDING = 'sale_pending'
    REDEMPTION = 'redemption'
    CANCEL = 'cancelation'
    REFUND = 'refund'

    CHOICES = (
        (PURCHASE, 'Purchase'),
        (PURCHASE_COMPLETED, 'Purchase Completed'),
        (SALE, 'Sale'),
        (SALE_PENDING, 'Pending Sale'),
        (REDEMPTION, 'Redeemed'),
        (CANCEL, 'Cancelled'),
        (REFUND, 'Refunded')
    )


class TransactionManager(QuickManager):
    """
    Nice dude.
    Code reviewed and approved.
    Thanks - Josie 3-12-2013
    """
    def create_purchase(
        self,
        **kwargs
    ):
        kwargs['transaction_type'] = TransactionTypes.PURCHASE
        transaction = super(TransactionManager, self).create(**kwargs)
        return transaction

    def create_purchase_completed(
        self,
        **kwargs
    ):
        kwargs['transaction_type'] = TransactionTypes.PURCHASE_COMPLETED
        transaction = super(TransactionManager, self).create(**kwargs)
        return transaction

    def crete_sale(
        self,
        **kwargs
    ):
        kwargs['transaction_type'] = TransactionTypes.SALE
        transaction = super(TransactionManager, self).create(**kwargs)
        return transaction

    def create_sale_pending(
        self,
        **kwargs
    ):
        kwargs['transaction_type'] = TransactionTypes.SALE_PENDING
        transaction = super(TransactionManager, self).create(**kwargs)
        return transaction

    def create_redemption(
        self,
        **kwargs
    ):
        kwargs['transaction_type'] = TransactionTypes.REDEMPTION
        transaction = super(TransactionManager, self).create(**kwargs)
        return transaction

    def create_cancelation(
        self,
        **kwargs
    ):
        kwargs['transaction_type'] = TransactionTypes.CANCEL
        transaction = super(TransactionManager, self).create(**kwargs)
        return transaction

    def create_refund(
        self,
        **kwargs
    ):
        kwargs['transaction_type'] = TransactionTypes.REFUND
        transaction = super(TransactionManager, self).create(**kwargs)
        return transaction

    def create(
        self,
        **kwargs
    ):
        create_methods = {}
        for transaction_type in TransactionTypes.choices:
            create_methods[transaction_type] = 'create_' + transaction_type

        create_methods[transaction_type](**kwargs)

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


class Transaction(KnotisModel):
    owner = QuickForeignKey(Identity)
    other = QuickForeignKey(Identity)

    transaction_type = QuickCharField(
        max_length=64,
        null=True,
        choices=TransactionTypes.CHOICES,
        db_index=True
    )

    offer = QuickForeignKey(Offer)

    sent = QuickForeignKey(Inventory)
    sent_value = QuickFloatField()

    recieved = QuickForeignKey(Inventory)
    recieved_value = QuickFloatField()

    transaction_context = QuickCharField(
        max_length=1024,
        null=True,
        blank=True,
        default=None,
        db_index=True
    )

    objects = TransactionManager()

    def __unicode__(self):
        return '/'.join([
            self.user.username if self.user else 'None',
            self.business.business_name.value if self.business else 'None',
            self.offer.id if self.offer else 'None',
            unicode(self.transaction_type),
            self.transaction_context
        ])

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
