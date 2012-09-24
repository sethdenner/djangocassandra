from django.db.models import IntegerField, FloatField, DateTimeField, \
    Manager, CharField
from django.contrib.auth.models import User
from knotis import KnotisModel
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.businesses import Business
from app.models.offers import Offer


class TransactionTypes:
    PURCHASE = 0
    REDEMPTION = 1
    CANCEL = 2
    REFUND = 3
    COMPLETE = 4
    
    CHOICES = (
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
        transaction_context=None,
        force_add=False  # if you are force adding you better be changing the date afterwards!!!
    ):
        if not force_add:
            try:
                existing = self.get(
                    user=user,
                    business=business,
                    offer=offer,
                    transaction_type=transaction_type,
                    transaction_context=transaction_context
                )
            except:
                existing = None
    
            if existing:
                raise ValueError('We already have a record of this transaction')

        return self.create(
            user=user,
            business=business,
            offer=offer,
            transaction_type=transaction_type,
            quantity=quantity,
            value=value,
            transaction_context=transaction_context
        )


class Transaction(KnotisModel):
    user = ForeignKeyNonRel(User)
    business = ForeignKeyNonRel(Business)
    offer = ForeignKeyNonRel(Offer)
    transaction_type = IntegerField(
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
