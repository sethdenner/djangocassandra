import logging
import datetime
import random
import re

from django.db.models import DateTimeField, IntegerField, \
    FloatField, NullBooleanField, CharField, Manager
from django.utils.http import urlquote
from django.conf import settings

from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content, ContentTypes
from app.models.businesses import Business
from app.models.endpoints import EndpointTypes, EndpointAddress
from app.models.cities import City
from app.models.neighborhoods import Neighborhood
from app.models.categories import Category
from app.models.media import Image


class OfferTypes:
    NORMAL = 0
    PREMIUM = 1

    CHOICES = (
        (NORMAL, 'Normal'),
        (PREMIUM, 'Premium')
    )


class OfferStatus:
    CREATED = 'created'
    CURRENT = 'current'
    COMPLETE = 'complete'

    CHOICES = (
        (CREATED, 'Created'),
        (CURRENT, 'Current'),
        (COMPLETE, 'Complete')
    )


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
        published,
        premium=False
    ):
        backend_name = urlquote(('offer_' + business.backend_name + '_' + title).strip().lower().replace(' ', '-'))

        content_root = Content.objects.create(
            content_type=ContentTypes.OFFER,
            user=user,
            name=backend_name
        )

        content_title = Content.objects.create(
            content_type=ContentTypes.OFFER_TITLE,
            user=user,
            name=backend_name,
            parent=content_root,
            value=title
        )

        content_description = Content.objects.create(
            content_type=ContentTypes.OFFER_DESCRIPTION,
            user=user,
            name=backend_name,
            parent=content_root,
            value=description
        )

        content_restrictions = Content.objects.create(
            content_type=ContentTypes.OFFER_RESTRICTIONS,
            user=user,
            name=backend_name,
            parent=content_root,
            value=restrictions
        )

        endpoint_address = EndpointAddress.objects.create(
            type=EndpointTypes.ADDRESS,
            user=user,
            value=address,
            primary=True,
        )

        offer = self.create(
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
            unlimited=unlimited,
            published=published,
            status=OfferStatus.CURRENT if published else OfferStatus.CREATED,
            active=published,
            premium=premium
        )

        if image:
            model_image = Image.objects.create(
                user=user,
                related_object_id=offer.id,
                image=image,
            )
            offer.image = model_image

        offer.save()

        if None != category and offer.active:
            category.active_offer_count = category.active_offer_count + 1
            category.save()

        return offer

    def get_offers_category_dict(self):
        categories = None
        try:
            categories = Category.objects.all()
        except:
            pass

        if not categories:
            return None

        results = {}

        for category in categories:
            try:
                offers = self.get_available_offers(category=category)
                if len(offers):
                    results[category.short_name()] = offers
            except:
                pass

        total = 0
        for key in results:
            total += len(results[key])

        results['total_offers'] = total

        return results

    def get_subscribed_businesses_offers_dict(
        self,
        subscriptions
    ):
        offers = {}
        for subscription in subscriptions:
            try:
                business = Business.objects.get(pk=subscription.business_id)
                offers[business.backend_name] = business
            except:
                pass

        for key in offers:
            try:
                offers[key] = self.get_available_offers(business=offers[key])
            except:
                offers.pop(key)

        return offers

    def _page_results(
        self,
        results,
        page
    ):
        if None == page:
            return results

        page_size = 20
        slice_start = (page - 1) * page_size
        slice_end = slice_start + page_size

        return results[slice_start:slice_end]

    def get_available_offers(
        self,
        city=None,
        neighborhood=None,
        category=None,
        business=None,
        premium=None,
        page=None
    ):
        try:
            results = self.filter(
                published=True,
                active=True,
                status=OfferStatus.CURRENT
            )
            if None != city:
                results = results.filter(city=city)
            if None != neighborhood:
                results = results.filter(neighborhood=neighborhood)
            if None != premium:
                results = results.filter(premium=premium)
            if None != category:
                results = results.filter(category=category)
            if None != business:
                results = results.filter(business=business)

            return self._page_results(
                results,
                page
            )

        except:
            return None

    def get_category_offers(
        self,
        category,
        page='1'
    ):
        page = int(page)

        results = None
        try:
            results = self.get_available_offers(
                category=category,
                page=page
            )
        except:
            pass

        return results

    def get_popular_offers(
        self,
        city_name=None,
        neighborhood_name=None,
        page=1
    ):
        offers = None
        try:
            offers = self.get_available_offers()
        except:
            pass

        if not offers:
            return None

        popular_offers = []
        for offer in offers:
            if offer.purchased > 3 and offer.last_purchase >= datetime.datetime.now() + datetime.timedelta(days= -1):
                popular_offers.append(offer)

        def get_popularity_sort_key(offer):
            return offer.last_purchase

        popular_offers = sorted(popular_offers, key=get_popularity_sort_key)

        return self._page_results(
            popular_offers,
            page
        )

    def get_premium_offers(
        self,
        city_name=None,
        neighborhood_name=None
    ):
        offers = None
        try:
            offers = self.get_available_offers(premium=True)
        except:
            pass

        if not offers:
            return None

        offers_list = list(offers)
        random.shuffle(offers_list)
        return offers_list[:5]

    def get_newest_offers(
        self,
        city_name=None,
        neighborhood_name=None,
        page=1
    ):
        offers = None
        try:
            offers = self.get_available_offers()
        except:
            pass

        if not offers:
            return None

        newest_offers = []
        for offer in offers:
            if offer.pub_date >= datetime.datetime.now() + datetime.timedelta(days= -1):
                newest_offers.append(offer)

        def get_newest_sort_key(offer):
            return offer.pub_date

        newest_offers = sorted(newest_offers, key=get_newest_sort_key)

        return self._page_results(
            newest_offers,
            page
        )

    def get_expiring_offers(
        self,
        city_name=None,
        neighborhood_name=None,
        page='1'
    ):
        offers = None
        try:
            offers = self.get_available_offers()
        except:
            pass

        if not offers:
            return None

        expiring_offers = []
        for offer in offers:
            if offer.end_date <= datetime.datetime.now() + datetime.timedelta(days=1):
                expiring_offers.append(offer)

        def get_expiring_sort_key(offer):
            return offer.end_date

        expiring_offers = sorted(expiring_offers, key=get_expiring_sort_key)

        return self._page_results(
            expiring_offers,
            page
        )

    def get_active_offer_count(self):
        offers = None
        try:
            offers = self.get_available_offers()
        except:
            pass

        if not offers:
            return 0
        else:
            return len(offers)

    def search_offers(
        self,
        query
    ):
        offers = None
        try:
            offers = self.get_available_offers()
        except:
            pass

        if not offers:
            return None

        query = query.lower().replace(
            ' ',
            ''
        )

        regex = re.compile(query, re.IGNORECASE)

        results = []
        for offer in offers:
            if regex.search(offer.title.value.lower().replace(' ', '')):
                results.append(offer)

        return results


class OfferTitleTypes:
    TITLE_1 = 1
    TITLE_2 = 2
    TITLE_3 = 3

    CHOICES = (
        (TITLE_1, 'Title 1'),
        (TITLE_2, 'Title 2'),
        (TITLE_3, 'Title 3'),
    )


class Offer(KnotisModel):
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

    start_date = DateTimeField(null=True, db_index=True)
    end_date = DateTimeField(null=True, db_index=True)

    status = CharField(
        max_length=32,
        choices=OfferStatus.CHOICES,
        db_index=True,
        default=OfferStatus.CREATED
    )
    stock = IntegerField(default=0, blank=True, null=True)
    purchased = IntegerField(default=0, blank=True, null=True)
    redeemed = IntegerField(default=0, blank=True, null=True)
    unlimited = NullBooleanField(default=False)

    published = NullBooleanField(default=False)
    active = NullBooleanField(default=False, db_index=True)
    premium = NullBooleanField(default=False, db_index=True)

    last_purchase = DateTimeField(null=True)
    pub_date = DateTimeField(null=True, auto_now_add=True)

    objects = OfferManager()

    def title_formatted(self):
        if not self.title:
            return ''

        if OfferTitleTypes.TITLE_1 == self.title_type:
            return ''.join([
                '$',
                self.price_discount_formatted(),
                ' for $',
                self.price_retail_formatted(),
                ' at ',
                self.business.business_name.value
            ])
        elif OfferTitleTypes.TITLE_2 == self.title_type:
            return ''.join([
                '$',
                self.price_discount_formatted(),
                ' for ',
                self.title.value,
                ' at ',
                self.business.business_name.value
            ])
        else:
            return self.title.value

    def description_100(self):
        if not self.description:
            return ''

        return ''.join([
            self.description.value[:97],
            '...'
        ])

    def price_retail_formatted(self):
        return ("%.2f" % round(
            self.price_retail,
            2
        )).replace('.00', '')

    def price_discount_formatted(self):
        return ("%.2f" % round(
            self.price_discount,
            2
        )).replace('.00', '')

    def savings(self):
        return ("%.2f" % round(
            self.price_retail - self.price_discount,
            2
        )).replace('.00', '')

    def savings_percent(self):
        return '%.0f' % round(
            (self.price_retail - self.price_discount) / self.price_retail * 100,
            0
        )

    def days_remaining(self):
        delta = self.end_date - self.start_date
        return delta.days

    def public_url(self):
        return settings.BASE_URL + '/offer/' + self.id + '/'

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
        published=None,
        status=None,
        purchased=None,
        redeemed=None,
        active=None,
        premium=None
    ):
        is_self_dirty = False

        if None != title:
            current_title = self.title.value if self.title else None
            if title != current_title:
                if self.title:
                    self.title = self.title.update(title)
                else:
                    self.title = Content.objects.create(
                        content_type=ContentTypes.OFFER_TITLE,
                        user=self.business.user,
                        name=self.content_root.name,
                        parent=self.content_root,
                        value=title
                    )
                is_self_dirty = True

        if None != description:
            current_description = self.description.value if self.description else None
            if description != current_description:
                if self.description:
                    self.description = self.description.update(description)
                else:
                    self.description = Content.objects.create(
                        content_type=ContentTypes.OFFER_DESCRIPTION,
                        user=self.business.user,
                        name=self.content_root.name,
                        parent=self.content_root,
                        value=description
                    )
                is_self_dirty = True

        if None != restrictions:
            current_restrictions = self.restrictions.value if self.restrictions else None
            if restrictions != current_restrictions:
                if self.restrictions:
                    self.restrictions = self.restrictions.update(restrictions)
                else:
                    self.restricitons = Content.objects.create(
                        content_type=ContentTypes.OFFER_RESTRICTIONS,
                        user=self.business.user,
                        name=self.content_root.name,
                        parent=self.content_root,
                        value=restrictions
                    )
                is_self_dirty = True

        if None != city and city != self.city:
            self.city = city
            is_self_dirty = True

        if None != neighborhood and neighborhood != self.neighborhood:
            self.neighborhood = neighborhood
            is_self_dirty = True

        if None != address:
            current_address = self.address.value.value if self.address else None
            if address != current_address:
                if self.address:
                    self.address.update(address)
                else:
                    self.address = EndpointAddress.objects.create(
                        user=self.business.user,
                        value=address
                    )
                    is_self_dirty = True

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

        if None != status and status != self.status:
            self.status = status
            is_self_dirty = True

        if None != purchased and purchased != self.purchased:
            self.purchased = purchased
            is_self_dirty = True

        if None != redeemed and redeemed != self.redeemed:
            self.redeemed = redeemed
            is_self_dirty = True

        if None != active and active != self.active:
            self.active = active
            is_self_dirty = True

            self.category.active_offer_count = \
                self.category.active_offer_count + (1 if active else -1)
            self.category.save()

        if None != premium and premium != self.premium:
            self.premium = premium
            is_self_dirty = True

        if is_self_dirty:
            self.save()
