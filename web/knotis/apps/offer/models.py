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
from django.utils.http import urlquote
from django.conf import settings

from knotis.utils.view import (
    format_currency,
    sanitize_input_html
)
from knotis.apps.cassandra.models import ForeignKey
from knotis.apps.core.models import KnotisModel
from knotis.apps.content.models import (
    Content,
    ContentTypes
)
from knotis.apps.business.models import Business
from knotis.apps.endpoint.models import (
    EndpointTypes,
    EndpointAddress
)
from knotis.apps.category.models import (
    City,
    Neighborhood,
    Category
)
from knotis.apps.media.models import Image


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
        premium=False,
        active=True
    ):
        backend_name = \
            urlquote(('offer_' + business.backend_name + '_' + title)\
                .strip()\
                .lower()\
                .replace(
                    ' ',
                    '-'
                )
            )

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
            image=image,
            category=category,
            price_retail=price_retail,
            price_discount=price_discount,
            start_date=start_date,
            end_date=end_date,
            stock=stock,
            unlimited=unlimited,
            published=published,
            status=OfferStatus.CURRENT if published else OfferStatus.CREATED,
            active=active,
            premium=premium
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
        business=None,
        city=None,
        neighborhood=None,
        category=None,
        premium=None,
        active=None,
        status=None,
        published=None,
        page=None,
        query=None,
        sort_by=OfferSort.NEWEST,
    ):
        try:
            results = self.filter(deleted=False)

            if None != business:
                results = results.filter(business=business)

            if None != city:
                results = results.filter(city=city)

            if None != neighborhood:
                results = results.filter(neighborhood=neighborhood)

            if None != category:
                results = results.filter(category=category)

            if None != premium:
                results = results.filter(premium=premium)

            if None != active:
                results = results.filter(active=active)

            if None != status:
                results = results.filter(status=status)

            if None != published:
                results = results.filter(published=published)

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

        except Exception as e:
            return None

    def get_available_offers(
        self,
        business=None,
        city=None,
        neighborhood=None,
        category=None,
        premium=None,
        page=None,
        query=None,
        sort_by=OfferSort.NEWEST
    ):
        return self.get_offers(
            business,
            city,
            neighborhood,
            category,
            premium,
            True,
            OfferStatus.CURRENT,
            True,
            page,
            query,
            sort_by
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
    business = ForeignKey(Business)
    offer_type = IntegerField(
        default=OfferTypes.NORMAL,
        choices=OfferTypes.CHOICES,
        null=True,
        blank=True
    )

    title = ForeignKey(Content, related_name='offer_title')
    title_type = IntegerField(
        choices=OfferTitleTypes.CHOICES,
        blank=True,
        null=True
    )
    description = ForeignKey(Content, related_name='offer_description')
    restrictions = ForeignKey(Content, related_name='offer_restrictions')

    city = ForeignKey(City)
    neighborhood = ForeignKey(Neighborhood)
    address = ForeignKey(EndpointAddress)

    image = ForeignKey(Image)
    category = ForeignKey(Category)

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
    deleted = NullBooleanField(default=False, db_index=True)

    last_purchase = DateTimeField(null=True, blank=True, default=None)
    pub_date = DateTimeField(null=True, auto_now_add=True)

    objects = OfferManager()

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
        if (self.end_date and self.end_date < datetime.datetime.utcnow()) or \
            (not self.unlimited and self.purchased >= self.stock):
            self.complete()

    def _update_offer_counts(
        self,
        delta
    ):
        if self.city:
            if self.city.active_offer_count:
                self.city.active_offer_count = \
                    self.city.active_offer_count + delta

                if self.city.active_offer_count < 0:
                    self.city.active_offer_count = 0

            else:
                self.city.active_offer_count = delta if delta > 0 else 0

            self.city.save()

        if self.neighborhood:
            if self.neighborhood.active_offer_count:
                self.neighborhood.active_offer_count = \
                    self.neighborhood.active_offer_count + delta

                if self.neighborhood.active_offer_count < 0:
                    self.neighborhood.active_offer_count = 0

            else:
                self.neighborhood.active_offer_count = \
                    delta if delta > 0 else 0

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

    def purchase(self):
        if not self.available():
            raise Exception('Could not purchase offer {%s}. Offer is not available' % (self.id,))

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
        if not self.description or not self.description.value:
            return ''

        return sanitize_input_html(
            self.description.value.replace(
                '\n',
                '<br/>'
            )
        )

    def restrictions_formatted_html(self):
        if not self.restrictions or not self.restrictions.value:
            return ''

        return sanitize_input_html(
            self.restrictions.value.replace(
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
                self.title.value,
                ' at ',
                self.business.business_name.value
            ])

        else:
            title_formatted = self.title.value

        return title_formatted.replace('\n', ' ')

    def description_javascript(self):
        if not self.description:
            return ''

        return self.description.value.replace(
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

        return self.title.value.replace(
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
            self.description.value[:97],
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
            (self.price_retail - self.price_discount) / \
                self.price_retail * 100,
            0
        )

    def days_remaining(self):
        delta = self.end_date - self.start_date
        return delta.days

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
        available = self.available()

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
            current_description = \
                self.description.value if self.description else None
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
            current_restrictions = \
                self.restrictions.value if self.restrictions else None
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
            current_address = \
                self.address.value.value if self.address else None
            if address != current_address:
                if self.address:
                    self.address.update(address)
                else:
                    self.address = EndpointAddress.objects.create(
                        user=self.business.user,
                        value=address
                    )
                    is_self_dirty = True

        if None != image and (None == self.image or image != self.image.image):
            self.image = image
            is_self_dirty = True

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

        if None != premium and premium != self.premium:
            self.premium = premium
            is_self_dirty = True

        if is_self_dirty:
            self.save()

        if available != self.available():
            delta = 1 if self.available() else -1
            self._update_offer_counts(delta)
