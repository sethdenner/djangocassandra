from django.contrib.auth.models import User, Group
from django.db.models import CharField, ForeignKey, DateTimeField, FloatField, IntegerField

from app.models.knotis import KnotisModel

from app.models.contents import Content
from app.models.products import Product
from app.models.businesses import Business
from app.models.establishment import Establishment
from app.models.accounts import Currency, AccountType, Account
from app.models.fields.permissions import PermissionsField
from app.models.fields.hours import HoursField

class OfferType(KnotisModel):
    OFFER_TYPES = (
        ('0', 'normal'),
    )

    value = CharField(max_length=30, choices=OFFER_TYPES)
    pub_date = DateTimeField('date published')
    def __unicode__(self):
        return self.name

class Offer(KnotisModel):
    establishment = ForeignKey(Establishment)
    offer_type = ForeignKey(OfferType)
    currency = ForeignKey(Currency)
    content = ForeignKey(Content)
    
    price_regular = FloatField()

    """ Some things may only be purchased by people with certain user_relationships. """
    permissions = PermissionsField() 

    """ When can this deal be purchased? """
    hours = HoursField()

    pub_date = DateTimeField('date published')

""" This is essentially the inventory. It has an associated hours field for allowing scheduled offers. """
class OfferInventory(KnotisModel):
    offer = ForeignKey(Offer)
    hours = HoursField()
    price = FloatField()
    available = IntegerField()
    total = IntegerField()
    sold = IntegerField()
