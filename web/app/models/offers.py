from django.db.models import CharField, DateTimeField, FloatField, IntegerField
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content
from app.models.products import Product
from app.models.establishments import Establishment
from app.models.accounts import Currency
#from app.models.fields.permissions import PermissionsField
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
    establishment = ForeignKeyNonRel(Establishment)
    offer_type = ForeignKeyNonRel(OfferType)
    currency = ForeignKeyNonRel(Currency)
    content = ForeignKeyNonRel(Content)

    price_regular = FloatField()

    """ Some things may only be purchased by people with certain user_relationships. """
    #permissions = ManyToManyField(Permission, null=True, blank=True)
    #permissions = PermissionsField()

    """ When can this deal be purchased? """
    hours = HoursField()

    pub_date = DateTimeField('date published')


class OfferProducts(KnotisModel):
    offer = ForeignKeyNonRel(Offer)
    product = ForeignKeyNonRel(Product)
    #How do we account for offers that are combined between businesse?


class OfferInventory(KnotisModel):
    """
    This is essentially the inventory. It has an associated hours field for allowing scheduled offers. 
    """
    offer = ForeignKeyNonRel(Offer)
    hours = HoursField()
    price = FloatField()
    available = IntegerField()
    total = IntegerField()
    sold = IntegerField()
