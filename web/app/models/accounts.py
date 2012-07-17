from django.contrib.auth.models import Group, User
from django.db.models import CharField, ForeignKey, DateTimeField, FloatField, BooleanField

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
    user = ForeignKey(User)
    account_type = ForeignKey(AccountType)
    currency = ForeignKey(Currency)
    business = ForeignKey(Business, null=True)
    content = ForeignKey(Content)
    name = CharField(max_length=140)
    funds_available = FloatField()
    pub_date = DateTimeField('date published')     # date created.
    updated_date = DateTimeField('date published') # last updated
    state = BooleanField()                         # later add an enum for (disabled etc.)
