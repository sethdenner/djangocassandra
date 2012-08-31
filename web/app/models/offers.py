from django.db.models import CharField, DateTimeField, FloatField, IntegerField
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content
from app.models.products import Product
from app.models.establishments import Establishment
from app.models.accounts import Currency


#from app.models.fields.permissions import PermissionsField
from app.models.fields.hours import HoursField

class Offer(KnotisModel):
    OFFER_TYPES = (
        ('0', 'normal'),             
    )
    
    establishment = ForeignKeyNonRel(Establishment)
    offer_type = CharField(max_length=100, choices=OFFER_TYPES, null=True)
    
    title = ForeignKeyNonRel(Content, related_name='offer_title')
    description = ForeignKeyNonRel(Content, related_name='offer_description')
    
    city = CharField(max_length=100)
    neighborhood = CharField(max_length=100)
    
    image_uri = CharField(max_length=1024, null=True, blank=True)
    category = CharField(max_length=100, null=True, blank=True)

    price_retail = FloatField(null=True)
    price_discount = FloatField(null=True)

    start_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)

    pub_date = DateTimeField(null=True, auto_now_add=True)
    
    @staticmethod
    def create(
        establishment,
        offer_type,
        title,
        description,
        city,
        neighborhood,
        image_uri,
        category,
        price_retail,
        price_discount,
        start_date,
        end_date
    ):
        pass
