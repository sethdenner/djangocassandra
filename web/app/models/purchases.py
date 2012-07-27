from django.contrib.auth.models import User
from django.db.models import CharField, DateTimeField, FloatField, BooleanField
from foreignkeynonrel.models import ForeignKeyNonRel

from app.models.knotis import KnotisModel
#from app.models.fields.permissions import PermissionsField
from app.models.contents import Content
from app.models.businesses import Business
from app.models.accounts import Currency, Account
from app.models.offers import Offer


class PurchaseType(KnotisModel):
    name = CharField(max_length=140)


class Purchase(KnotisModel):
    user = ForeignKeyNonRel(User)
    offer = ForeignKeyNonRel(Offer)
    source_account = ForeignKeyNonRel(Account, related_name='account_source_account')
    dest_account = ForeignKeyNonRel(Account, related_name='account_destination_account')
    purchasetype = ForeignKeyNonRel(PurchaseType)
    currency = ForeignKeyNonRel(Currency)
    b_parent = ForeignKeyNonRel(Business)
    c_parent = ForeignKeyNonRel(Content)
    o_name = CharField(max_length=140)
    value = FloatField()
    pub_date = DateTimeField('date published')
    state = BooleanField() # later an enum for (disabled etc.)
