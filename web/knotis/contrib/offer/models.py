import re
import datetime

from django.db.models import (
    DateTimeField,
    IntegerField,
    FloatField,
    NullBooleanField,
    CharField,
    Manager
)
from django.conf import settings
from knotis.contrib.quick.models import (
    QuickModel
)
from knotis.contrib.quick.fields import (
    QuickForeignKey,
    QuickDateTimeField,
    QuickIntegerField,
    QuickCharField,
    QuickFloatField
)
from knotis.utils.view import (
    format_currency,
    sanitize_input_html
)
from knotis.contrib.cassandra.models import ForeignKey
from knotis.contrib.core.models import KnotisModel
from knotis.contrib.business.models import Business
from knotis.contrib.media.models import Image
from knotis.contrib.category.models import (
    Category,
    City,
    Neighborhood
)
from knotis.contrib.identity.models import Identity
from knotis.contrib.product.models import Product
from knotis.contrib.inventory.models import Inventory


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


class OfferSort:
    NEWEST = 'newest'
    EXPIRING = 'expiring'
    POPULAR = 'popular'

    CHOICES = (
        (NEWEST, 'Newest'),
        (EXPIRING, 'Expiring'),
        (POPULAR, 'Popular')
    )


class OfferManager(Manager):
    def create_offer(
        self,
        owner,
        title,
        title_type,
        description,
        restrictions,
        city,
        neighborhood,
        image,
        category,
        price_retail,
        price_discount,
        currency,
        start_date,
        end_date,
        stock,
        unlimited,
        published,
        premium=False,
        active=True,
        inventory=[]
    ):
        offer = Offer(
            owner=owner,
            title=title,
            title_type=title_type,
            description=description,
            image=image,
            category=category,
            city=city,
            neighborhood=neighborhood,
            price_retail=price_retail,
            price_discount=price_discount,
            currency=currency,
            published=published,
            status=OfferStatus.CURRENT if published else OfferStatus.CREATED,
            active=active,
            premium=premium,
            restrictions=restrictions,
            stock=stock,
            unlimited=unlimited,
            start_date=start_date,
            end_date=end_date
        )
        offer.visable = offer.is_visable()
        offer.searchable = offer.is_searchable()
        offer.purchasable = offer.is_purchaseable()
        offer.save()

        for i in inventory:
            OfferItem.objects.create(
                offer=offer,
                inventory=i,
                price_discount=price_discount
            )

        if image:
            image.related_object_id = offer.id
            image.save()

        if offer.available():
            offer._update_offer_counts(1)

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

        if isinstance(page, basestring):
            try:
                page = int(page)
            except:
                page = 1

        page_size = 20
        slice_start = (page - 1) * page_size
        slice_end = slice_start + page_size

        return results[slice_start:slice_end]

    def get_offers(
        self,
        filters={},
        page=None,
        query=None,
        sort_by=OfferSort.NEWEST,
    ):
        try:
            filters['deleted'] = False
            results = self.filter(filters)

            if not len(results):
                return results

            if query:
                query_words = query.split(' ')

                query_results = []
                for offer in results:
                    for word in query_words:
                        if not word:
                            continue

                        regex = re.compile(
                            word.strip(),
                            re.IGNORECASE
                        )
                        if regex.search(offer.title.value):
                            query_results.append(offer)

                results = query_results

            if OfferSort.NEWEST == sort_by:
                def get_newest_sort_key(offer):
                    return offer.pub_date

                results = sorted(
                    results,
                    key=get_newest_sort_key
                )
                results.reverse()

            elif OfferSort.POPULAR == sort_by:
                def get_popularity_sort_key(offer):
                    return offer.last_purchase

                results = sorted(
                    results,
                    key=get_popularity_sort_key
                )
                results.reverse()

            elif OfferSort.EXPIRING == sort_by:
                def get_expiring_sort_key(offer):
                    return offer.end_date

                results = sorted(
                    results,
                    key=get_expiring_sort_key
                )

            return self._page_results(
                results,
                page
            )

        except Exception:
            return None

    def get_available_offers(
        self,
        filters={},
        page=None,
        query=None,
        sort_by=OfferSort.NEWEST
    ):
        filters['active'] = True
        filters['status'] = OfferStatus.CURRENT
        filters['published'] = True

        return self.get_offers(
            filters=filters,
            page=page,
            query=query,
            sort_by=sort_by
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
        query,
        business=None,
        city=None,
        neighborhood=None,
        category=None,
        premium=None,
        page=None,
        sort_by=OfferSort.NEWEST
    ):
        offers = None
        try:
            offers = self.get_available_offers(
                business,
                city,
                neighborhood,
                category,
                premium,
                None,
                sort_by
            )
        except:
            pass

        if not offers:
            return None

        if not query:
            return offers

        query_words = query.split(' ')

        results = []
        for offer in offers:
            for word in query_words:
                if not word:
                    continue

                regex = re.compile(
                    word.strip(),
                    re.IGNORECASE
                )
                if regex.search(offer.title.value):
                    results.append(offer)

        return self._page_results(
            results,
            page
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


class Offer(KnotisModel):
    owner = ForeignKey(Identity)
    offer_type = IntegerField(
        default=OfferTypes.NORMAL,
        choices=OfferTypes.CHOICES,
        null=True,
        blank=True
    )

    title = CharField(
        null=True,
        blank=True,
        default=None,
        max_length=140
    )
    title_type = IntegerField(
        choices=OfferTitleTypes.CHOICES,
        blank=True,
        null=True
    )
    description = CharField(
        null=True,
        blank=True,
        default=None,
        max_length=1024
    )

    image = ForeignKey(Image)
    category = ForeignKey(Category)
    city = ForeignKey(City)
    neighborhood = ForeignKey(Neighborhood)

    price_retail = FloatField(default=0., blank=True, null=True)
    price_discount = FloatField(default=0., blank=True, null=True)
    currency = ForeignKey(Product)

    status = CharField(
        max_length=32,
        choices=OfferStatus.CHOICES,
        db_index=True,
        default=OfferStatus.CREATED
    )
    redeemed = IntegerField(default=0, blank=True, null=True)
    published = NullBooleanField(default=False)
    active = NullBooleanField(default=False, db_index=True)
    premium = NullBooleanField(default=False, db_index=True)
    deleted = NullBooleanField(default=False, db_index=True)

    restrictions = QuickCharField(
        max_length=1024
    )
    stock = QuickIntegerField(
        default=0,
        blank=True,
        null=True
    )
    unlimited = NullBooleanField(
        default=False,
        blank=True,
        null=True
    )
    purchased = QuickIntegerField(
        default=0,
        blank=True,
        null=True
    )
    last_purchase = QuickDateTimeField(
        null=True,
        blank=True,
        default=None
    )
    start_date = QuickDateTimeField()
    end_date = QuickDateTimeField()

    pub_date = DateTimeField(null=True, auto_now_add=True)

    objects = OfferManager()

    visable = NullBooleanField()
    searchable = NullBooleanField()
    purchasable = NullBooleanField()

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(Offer, self).__init__(
            *args,
            **kwargs
        )

        # Could have no end date I guess so check for not None.
        if (
            self.end_date and self.end_date < datetime.datetime.utcnow()
        ) or (
            not self.unlimited and self.purchased >= self.stock
        ):
            self.complete()

    def _update_offer_counts(
        self,
        delta
    ):
        if self.city:
            if self.city.active_offer_count:
                self.city.active_offer_count = (
                    self.city.active_offer_count + delta
                )

                if self.city.active_offer_count < 0:
                    self.city.active_offer_count = 0

            else:
                self.city.active_offer_count = delta if delta > 0 else 0

            self.city.save()

        if self.neighborhood:
            if self.neighborhood.active_offer_count:
                self.neighborhood.active_offer_count = (
                    self.neighborhood.active_offer_count + delta
                )

                if self.neighborhood.active_offer_count < 0:
                    self.neighborhood.active_offer_count = 0

            else:
                self.neighborhood.active_offer_count = (
                    delta if delta > 0 else 0
                )

            self.neighborhood.save()

        if self.category:
            if self.category.active_offer_count:
                self.category.active_offer_count = \
                    self.category.active_offer_count + delta

                if self.category.active_offer_count < 0:
                    self.category.active_offer_count = 0

            else:
                self.category.active_offer_count = delta if delta > 0 else 0

            self.category.save()

    def is_visable(self):
        return True

    def is_searchable(self):
        return True

    def is_purchasable(self):
        return True

    def purchase(self):
        if not self.available():
            raise Exception(
                'Could not purchase offer {%s}. Offer is not available' % (
                    self.id,
                )
            )

        self.purchased = self.purchased + 1
        self.last_purchase = datetime.datetime.utcnow()
        self.save()

        if self.purchased == self.stock:
            self.complete()

    def complete(self):
        available = self.available()

        self.status = OfferStatus.COMPLETE
        self.save()

        if available:
            self._update_offer_counts(-1)

    def delete(self):
        available = self.available()

        self.deleted = True
        self.save()

        if available:
            self._update_offer_counts(-1)

    def available(self):
        now = datetime.datetime.utcnow()

        return self.active and \
            self.published and \
            self.status == OfferStatus.CURRENT and \
            self.start_date < now and \
            self.end_date > now and \
            self.purchased < self.stock

    def description_formatted_html(self):
        if not self.description:
            return ''

        return sanitize_input_html(
            self.description.replace(
                '\n',
                '<br/>'
            )
        )

    def restrictions_formatted_html(self):
        if not self.restrictions:
            return ''

        return sanitize_input_html(
            self.restrictions.replace(
                '\n',
                '<br/>'
            )
        )

    def title_formatted(self):
        if not self.title:
            return ''

        title_formatted = None
        if OfferTitleTypes.TITLE_1 == self.title_type:
            title_formatted = ''.join([
                '$',
                self.price_discount_formatted(),
                ' for $',
                self.price_retail_formatted(),
                ' at ',
                self.business.business_name.value
            ])

        elif OfferTitleTypes.TITLE_2 == self.title_type:
            title_formatted = ''.join([
                '$',
                self.price_discount_formatted(),
                ' for ',
                self.title,
                ' at ',
                self.business.business_name.value
            ])

        else:
            title_formatted = self.title

        return title_formatted.replace('\n', ' ')

    def description_javascript(self):
        if not self.description:
            return ''

        return self.description.replace(
            '\'',
            '\\\''
        ).replace(
            '"',
            '\\"'
        ).replace(
            '\n',
            ''
        )

    def title_javascript(self):
        if not self.title:
            return ''

        return self.title.replace(
            '\'',
            '\\\''
        ).replace(
            '"',
            '\\"'
        ).replace(
            '\n',
            ''
        )

    def title_short(self):
        if not self.title:
            return ''

        return ''.join([
            self.title_javascript()[:16],
            '...'
        ])

    def description_100(self):
        if not self.description:
            return ''

        return ''.join([
            self.description[:97],
            '...'
        ]).replace('\n', ' ')

    def price_retail_formatted(self):
        return format_currency(self.price_retail)

    def price_discount_formatted(self):
        return format_currency(self.price_discount)

    def savings(self):
        return format_currency(
            self.price_retail - self.price_discount
        )

    def savings_percent(self):
        return '%.0f' % round(
            (self.price_retail - self.price_discount) /
            self.price_retail * 100, 0
        )

    def days_remaining(self):
        delta = self.end_date - datetime.datetime.utcnow()
        return delta.days

    def stock_remaining(self):
        return self.stock - self.purchased

    def public_url(self):
        return '/'.join([
            settings.BASE_URL,
            'offer',
            self.id,
            ''
        ])

    def stock_values(self):
        if self.unlimited:
            return [i for i in range(1, 100)]

        else:
            stock_remaining = self.stock - self.purchased
            return [i for i in range(1, stock_remaining + 1)]

    def income_gross(self):
        return (self.purchased * self.price_discount)

    def income_net_formatted(self):
        gross = self.income_gross()
        our_cut = gross * .03
        return format_currency(gross - our_cut)


class OfferItem(QuickModel):
    offer = QuickForeignKey(Offer)
    inventory = QuickForeignKey(Inventory)
    price_discount = QuickFloatField()
