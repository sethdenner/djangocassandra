from django.db.models import CharField, DateTimeField, FloatField, Manager
from django.utils.http import urlquote
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content
from app.models.products import Product
from app.models.establishments import Establishment
from app.models.accounts import Currency
from app.models.endpoints import EndpointAddress
from app.models.cities import City
from app.models.neighborhoods import Neighborhood
from app.models.categories import Category
from app.models.images import Image


#from app.models.fields.permissions import PermissionsField
from app.models.fields.hours import HoursField

class OfferManager(Manager):
    def create_offer(
        user,
        establishment,
        offer_type,
        title,
        description,
        restrictions,
        city,
        neighborhood,
        address,
        image,
        category,
        price_retail,
        price_discount,
        start_date,
        end_date
    ):
        backend_name = urlquote(('offer_' + establishment.name + '_' + title).strip().lower().replace(' ', '-'))

        content_root = Content(
            content_type='8.0',
            user=user,
            name=backend_name
        )
        content_root.save()

        content_title = Content(
            content_type='8.1',
            user=user,
            name=backend_name,
            parent=content_root,
            value=title
        )
        content_title.save()

        content_description = Content(
            content_type='8.2',
            user=user,
            name=backend_name,
            parent=content_root,
            value=description
        )
        content_description.save()

        content_restrictions = Content(
            content_type='8.3',
            user=user,
            name=backend_name,
            parent=content_root,
            value=restrictions
        )
        content_restrictions.save()

        offer = Offer(
            establishment=establishment,
            offer_type='0',
            title=content_title,
            description=content_description,
            restrictions=content_restrictions,
            city=city,
            neighborhood=neighborhood,
            address=address,
            image=image,
            category=category,
            price_retail=price_retail,
            price_discount=price_discount,
            start_date=start_date,
            end_date=end_date
        )
        offer.save()


class Offer(KnotisModel):
    OFFER_TYPES = (
        ('0', 'normal'),
    )

    establishment = ForeignKeyNonRel(Establishment)
    offer_type = CharField(max_length=100, choices=OFFER_TYPES, null=True)

    title = ForeignKeyNonRel(Content, related_name='offer_title')
    description = ForeignKeyNonRel(Content, related_name='offer_description')
    restrictions = ForeignKeyNonRel(Content, related_name='offer_restrictions')

    city = ForeignKeyNonRel(City)
    neighborhood = ForeignKeyNonRel(Neighborhood)
    address = ForeignKeyNonRel(EndpointAddress)

    image = ForeignKeyNonRel(Image)
    category = CharField(max_length=100, null=True, blank=True)

    price_retail = FloatField(null=True)
    price_discount = FloatField(null=True)

    start_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)

    pub_date = DateTimeField(null=True, auto_now_add=True)
