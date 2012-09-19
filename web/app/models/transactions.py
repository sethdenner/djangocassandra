from django.db.models import IntegerField, FloatField, DateTimeField, Manager
from django.contrib.auth.models import User
from knotis import KnotisModel
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.businesses import Business
from app.models.offers import Offer


class TransactionTypes:
    PURCHASE = 0
    REDEMPTION = 1
    PURCHASE_KNOTIS_UNLIMITED = 2

    CHOICES = (
        (PURCHASE, 'Purchase'),
        (REDEMPTION, 'Redemption'),
        (PURCHASE_KNOTIS_UNLIMITED, 'Purchase Knotis Unlimited')
    )


class TransactionManager(Manager):
    def create_transaction(
        self,
        user,
        transaction_type,
        business='knotis',
        offer=None,
        quantity=1,
        value=0.
    ):
        return self.create(
            user=user,
            business=business,
            offer=offer,
            transaction_type=transaction_type,
            quantity=quantity,
            value=value
        )


class Transaction(KnotisModel):
    user = ForeignKeyNonRel(User)
    business = ForeignKeyNonRel(Business)
    offer = ForeignKeyNonRel(Offer)
    transaction_type = IntegerField(null=True, choices=TransactionTypes.CHOICES)
    quantity = IntegerField(null=True)
    value = FloatField(blank=True, null=True, default=0.)
    pub_date = DateTimeField(auto_now_add=True)

    objects = TransactionManager()
