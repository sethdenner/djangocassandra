from django.db import models
from contents.models import Content
from product.models import Products
from businesses.models import Business
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from accounts.models import Currency
from accounts.models import AccountType
from accounts.models import Account

class OfferType(models.Model):
    name = models.CharField(max_length=140)

class Offer(models.Model):
#    parent_id = model.IntField()
#    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
    user = models.ForeignKey(User)
    offertype = models.ForeignKey(OfferType)
    currency = models.ForeignKey(Currency)
    b_parent = models.ForeignKey(Business)
    c_parent = models.ForeignKey(Content)
    o_name = models.CharField(max_length=140)
    content = models.FloatField()
    inventory = models.FloatField() #FIXME: think about this? How do we want to handle these types of values?
    pub_date = models.DateTimeField('date published')
    start_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date published')
# expiration, scheduled offers? Ticktes? Specific limited edition items? What about variety of inventory?
