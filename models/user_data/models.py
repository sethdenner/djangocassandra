from django.db import models

from contents.models import Content
from product.models import Products
from businesses.models import Business
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class UserEmail(models.Model):
    email = models.CharField(max_length=140)
    priority = models.IntField()
    confirmed = models.CharField(max_length=140)
    pub_date = models.DateTimeField('date published') # date created.
    updated_date = models.DateTimeField('date published') # last updated
    state = models.BoolField() # later an enum for (disabled etc.) Create your models here.

class UserAddress(models.Model):
#    parent_id = model.IntField()
#    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
# There defidinetyl needs to be a lot more logic going on in here...
#    user = models.ForeignKey(User)
#    accounttype = models.ForeignKey(OfferType)
#    currency = models.ForeignKey(Currency)
#    b_parent = models.ForeignKey(Business)
#    c_parent = models.ForeignKey(Content)
#    name = models.CharField(max_length=140)
#    value = models.FloatField() #FIXME: think about this? How do we want to handle these types of values?
#    value_yesterday = models.FloatField() #FIXME: this is just one way we can check to see if the data is consistent?
#    pub_date = models.DateTimeField('date published') # date created.
#    updated_date = models.DateTimeField('date published') # last updated
#    state = models.BoolField() # later an enum for (disabled etc.) Create your models here.
