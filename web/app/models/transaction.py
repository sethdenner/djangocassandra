#from django.contrib.auth.models import User
#from django.db.models import CharField, DateTimeField, FloatField, BooleanField
from foreignkeynonrel.models import ForeignKeyNonRel

from app.models.knotis import KnotisModel

#from app.models.fields.permissions import PermissionsField

from app.models.offers import Offer
from app.models.accounts import Currency, Account


class Transaction(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    source_account = ForeignKeyNonRel(Account, related_name='account_source_account')
    dest_account = ForeignKeyNonRel(Account, related_name='account_destination_account')
    offer = ForeignKeyNonRel(Offer)
    currency = ForeignKeyNonRel(Currency)
