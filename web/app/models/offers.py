from django.db import models
from web.app.knotis.db import KnotisModel
from contents import Content
from products import Product
from businesses import Business
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from accounts import Currency, AccountType, Account

class OfferType(KnotisModel):
    OFFER_TYPES = (
        ('0', '____'),
        ('1', '____'),
        ('2', '____')
    )

    value = CharField(max_length=30, choices=ENDPOINT_PERMISSION_TYPES)
    #created_by = CharField(max_length=1024)
    pub_date = models.DateTimeField('date published')
    def __unicode__(self):
        return self.name

class Offer(KnotisModel):
#    parent_id = model.IntField()
#    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
    establishment = models.ForeignKey(Establishment)
    offer_type = models.ForeignKey(OfferType)
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
