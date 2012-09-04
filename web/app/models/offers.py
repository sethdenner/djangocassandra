from datetime import datetime

from django.db.models import DateTimeField, IntegerField, \
    FloatField, BooleanField, Manager
from django.utils.http import urlquote
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content
from app.models.businesses import Business
from app.models.endpoints import EndpointAddress
from app.models.cities import City
from app.models.neighborhoods import Neighborhood
from app.models.categories import Category
from app.models.images import Image


class OfferManager(Manager):
    def create_offer(
        self,
        user,
        business,
        title,
        title_type,
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
        end_date,
        stock,
        unlimited,
        published
    ):
        backend_name = urlquote(('offer_' + business.name + '_' + title).strip().lower().replace(' ', '-'))

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
            business=business,
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
            end_date=end_date,
            stock=stock,
            published=published,
            unlimited=unlimited
        )
        offer.save()

        return offer


class Offer(KnotisModel):
    NORMAL = 0
    OFFER_TYPES = (
        (NORMAL, 'normal'),
    )

    TITLE_1 = 1
    TITLE_2 = 2
    TITLE_3 = 3

    OFFER_TITLE_TYPES = (
        (TITLE_1, 'Title 1'),
        (TITLE_2, 'Title 2'),
        (TITLE_3, 'Title 3'),
    )

    business = ForeignKeyNonRel(Business)
    offer_type = IntegerField(choices=OFFER_TYPES, null=True, blank=True)

    title = ForeignKeyNonRel(Content, related_name='offer_title')
    title_type = IntegerField(choices=OFFER_TITLE_TYPES, blank=True, null=True)
    description = ForeignKeyNonRel(Content, related_name='offer_description')
    restrictions = ForeignKeyNonRel(Content, related_name='offer_restrictions')

    city = ForeignKeyNonRel(City)
    neighborhood = ForeignKeyNonRel(Neighborhood)
    address = ForeignKeyNonRel(EndpointAddress)

    image = ForeignKeyNonRel(Image)
    category = ForeignKeyNonRel(Category)

    price_retail = FloatField(default=0., blank=True, null=True)
    price_discount = FloatField(default=0., blank=True, null=True)

    start_date = DateTimeField(
        default=datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
        null=True
    )
    end_date = DateTimeField(
        default=datetime.now().replace(day=datetime.today().day + 7).strftime('%m/%d/%Y %H:%M:%S'),
        null=True
    )

    stock = IntegerField(default=0, blank=True, null=True)
    purchased = IntegerField(default=0, blank=True, null=True)
    unlimited = BooleanField(default=False)

    published = BooleanField(default=False)

    pub_date = DateTimeField(null=True, auto_now_add=True)

    objects = OfferManager()
