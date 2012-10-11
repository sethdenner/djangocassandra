import datetime
import itertools

from django.db.models import (
    IntegerField,
    FloatField,
    DateTimeField,
    Manager,
    CharField
)

from knotis.utils.view import format_currency
from knotis.apps.auth.models import KnotisUser
from knotis.apps.core.models import KnotisModel
from knotis.apps.cassandra.models import ForeignKey
from knotis.apps.business.models import Business
from knotis.apps.offer.models import Offer


class TransactionTypes:
    PENDING = 'pending'
    PURCHASE = 'purchase'
    REDEMPTION = 'redemption'
    CANCEL = 'cancel'
    REFUND = 'refund'

    CHOICES = (
        (PENDING, 'Pending'),
        (PURCHASE, 'Purchased'),
        (REDEMPTION, 'Redeemed'),
        (CANCEL, 'Cancelled'),
        (REFUND, 'Refunded')
    )


class TransactionManager(Manager):
    def create_transaction(
        self,
        user,
        transaction_type,
        business=None,
        offer=None,
        quantity=1,
        value=0.,
        transaction_context=None
    ):
        return self.create(
            user=user,
            business=business,
            offer=offer,
            transaction_type=transaction_type,
            quantity=quantity,
            value=value,
            transaction_context=transaction_context
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


class Transaction(KnotisModel):
    user = ForeignKey(KnotisUser)
    business = ForeignKey(Business)
    offer = ForeignKey(Offer)
    transaction_type = CharField(
        max_length=64,
        null=True,
        choices=TransactionTypes.CHOICES,
        db_index=True
    )
    quantity = IntegerField(null=True)
    value = FloatField(blank=True, null=True, default=0.)
    transaction_context = CharField(
        max_length=1024,
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    pub_date = DateTimeField(
        auto_now_add=True,
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
        return format_currency(self.value)

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
