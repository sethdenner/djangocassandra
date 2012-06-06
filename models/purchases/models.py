from django.db import models
from contents.models import Content
from product.models import Products
from businesses.models import Business
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from accounts.models import Currency
from accounts.models import AccountType
from accounts.models import Account
from offer.models import Offer

class PurchaseType(models.Model):
    name = models.CharField(max_length=140)

class Purchase(models.Model):
#    parent_id = model.IntField()
#    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
    user = models.ForeignKey(User)
    offer = models.ForeignKey(Offer)
    source_account = models.ForeignKey(Account)
    dest_account = models.ForeignKey(Account)
    offer = models.ForeignKey(Offer)
    purchasetype = models.ForeignKey(PurchaseType)
    currency = models.ForeignKey(Currency)
    b_parent = models.ForeignKey(Business)
    c_parent = models.ForeignKey(Content)
    o_name = models.CharField(max_length=140)
    value = models.FloatField()
    pub_date = models.DateTimeField('date published')
    state = models.BoolField() # later an enum for (disabled etc.)
