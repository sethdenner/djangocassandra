from django.contrib.auth.models import Group, User
from django.db.models import CharField, ForeignKey, DateTimeField, FloatField, BooleanField

from app.models.knotis import KnotisModel
from app.models.fields.permissions import PermissionsField
from app.models.contents import Content
from app.models.endpoints import Endpoint
from app.models.businesses import Business
from app.models.accounts import Currency, AccountType, Account
from app.models.offers import Offer

class PurchaseType(KnotisModel):
    name = CharField(max_length=140)

class Purchase(KnotisModel):
#    parent_id = model.IntField()
#    parent_type = CharField(max_length=200) # probably a stupid way to do this.
    user = ForeignKey(User)
    offer = ForeignKey(Offer)
    source_account = ForeignKey(Account)
    # FIXME: why can't we have multiple references to the same table?
    # dest_account = ForeignKey(Account)
    offer = ForeignKey(Offer)
    purchasetype = ForeignKey(PurchaseType)
    currency = ForeignKey(Currency)
    b_parent = ForeignKey(Business)
    c_parent = ForeignKey(Content)
    o_name = CharField(max_length=140)
    value = FloatField()
    pub_date = DateTimeField('date published')
    state = BooleanField() # later an enum for (disabled etc.)
