from django.contrib.auth.models import Group, User
from django.db.models import CharField, DateTimeField, FloatField, BooleanField
from foreignkeynonrel.models import ForeignKeyNonRel

from app.models.knotis import KnotisModel
#from app.models.fields.permissions import PermissionsField

from contents import Content
from products import Product
from businesses import Business


class Currency(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        
    name = CharField(max_length=140)

class AccountType(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = 'Account Type'
        verbose_name_plural = 'Account Types'
        
    name = CharField(max_length=140)

"""
There needs to be quite a bit more thought put into this and it definitely needs to be unit tested.

This is pretty much where the accounting system leaves off.
"""
class Account(KnotisModel):
    user = ForeignKeyNonRel(User)
    account_type = ForeignKeyNonRel(AccountType)
    currency = ForeignKeyNonRel(Currency)
    business = ForeignKeyNonRel(Business, null=True)
    content = ForeignKeyNonRel(Content)
    name = CharField(max_length=140)
    funds_available = FloatField()
    pub_date = DateTimeField('date published')     # date created.
    updated_date = DateTimeField('date published') # last updated
    state = BooleanField()                         # later add an enum for (disabled etc.)
