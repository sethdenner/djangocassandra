from datetime import datetime

from django.db.models import DateTimeField, IntegerField, \
    FloatField, BooleanField, Manager
from django.utils.http import urlquote
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content
from app.models.businesses import Business
from app.models.endpoints import Endpoint, EndpointAddress
from app.models.cities import City
from app.models.neighborhoods import Neighborhood
from app.models.categories import Category
from app.models.media import Image


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
        backend_name = urlquote(('offer_' + business.backend_name + '_' + title).strip().lower().replace(' ', '-'))

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

        endpoint_address = EndpointAddress(
            type=Endpoint.EndpointTypes.ADDRESS,
            user=user,
            value=address,
            primary=True,
        )
        endpoint_address.save()


        offer = Offer(
            business=business,
            title=content_title,
            title_type=title_type,
            description=content_description,
            restrictions=content_restrictions,
            city=city,
            neighborhood=neighborhood,
            address=endpoint_address,
            category=category,
            price_retail=price_retail,
            price_discount=price_discount,
            start_date=start_date,
            end_date=end_date,
            stock=stock,
            published=published,
            unlimited=unlimited
        )

        model_image = Image(
            user=user,
            related_object_id=offer.id,
            image=image,
        )
        model_image.save()

        offer.image = model_image
        offer.save()

        return offer


class Offer(KnotisModel):
    class OfferTypes:
        NORMAL = 0

        CHOICES = (
            (NORMAL, 'normal'),
        )

    class OfferTitleTypes:
        TITLE_1 = 1
        TITLE_2 = 2
        TITLE_3 = 3

        CHOICES = (
            (TITLE_1, 'Title 1'),
            (TITLE_2, 'Title 2'),
            (TITLE_3, 'Title 3'),
        )

    business = ForeignKeyNonRel(Business)
    offer_type = IntegerField(default=OfferTypes.NORMAL, choices=OfferTypes.CHOICES, null=True, blank=True)

    title = ForeignKeyNonRel(Content, related_name='offer_title')
    title_type = IntegerField(choices=OfferTitleTypes.CHOICES, blank=True, null=True)
    description = ForeignKeyNonRel(Content, related_name='offer_description')
    restrictions = ForeignKeyNonRel(Content, related_name='offer_restrictions')

    city = ForeignKeyNonRel(City)
    neighborhood = ForeignKeyNonRel(Neighborhood)
    address = ForeignKeyNonRel(EndpointAddress)

    image = ForeignKeyNonRel(Image)
    category = ForeignKeyNonRel(Category)

    price_retail = FloatField(default=0., blank=True, null=True)
    price_discount = FloatField(default=0., blank=True, null=True)

    start_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)

    stock = IntegerField(default=0, blank=True, null=True)
    purchased = IntegerField(default=0, blank=True, null=True)
    unlimited = BooleanField(default=False)

    published = BooleanField(default=False)

    pub_date = DateTimeField(null=True, auto_now_add=True)

    objects = OfferManager()

    def update(
        self,
        title=None,
        title_type=None,
        description=None,
        restrictions=None,
        city=None,
        neighborhood=None,
        address=None,
        image=None,
        category=None,
        price_retail=None,
        price_discount=None,
        start_date=None,
        end_date=None,
        stock=None,
        unlimited=None,
        published=None
    ):
        is_self_dirty = False

        if None != title and title != self.title.value:
            self.title.value = title
            self.title.save()

        if None != title_type and title_type != self.title_type:
            self.title_type = title_type
            is_self_dirty = True

        if None != description and description != self.description.value:
            self.description.value = description
            self.description.save()

        if None != restrictions and restrictions != self.restrictions.value:
            self.restrictions.value = restrictions
            self.restrictions.save()

        if None != city and city != self.city:
            self.city = city
            is_self_dirty = True

        if None != neighborhood and neighborhood != self.neighborhood:
            self.neighborhood = neighborhood
            is_self_dirty = True

        if None != address and address != self.address.value.value:
            self.address.value.value = address
            self.address.value.save()

        if None != image and image != self.image.image:
            self.image.image = image
            self.image.save()

        if None != category and category != self.category:
            self.category = category
            is_self_dirty = True

        if None != price_retail and price_retail != self.price_retail:
            self.price_retail = price_retail
            is_self_dirty = True

        if None != price_discount and price_discount != self.price_discount:
            self.price_discount = price_discount
            is_self_dirty = True

        if None != start_date and start_date != self.start_date:
            self.start_date = start_date
            is_self_dirty = True

        if None != end_date and end_date != self.end_date:
            self.end_date = end_date
            is_self_dirty = True

        if None != stock and stock != self.stock:
            self.stock = stock
            is_self_dirty = True

        if None != unlimited and unlimited != self.unlimited:
            self.unlimited = unlimited
            is_self_dirty = True

        # Don't allow to unpublish
        if published:
            self.published = published
            is_self_dirty = True

        if is_self_dirty:
            self.save()
