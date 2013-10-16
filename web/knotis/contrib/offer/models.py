import re
import datetime

from django.conf import settings
from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickForeignKey,
    QuickDateTimeField,
    QuickIntegerField,
    QuickCharField,
    QuickFloatField,
    QuickBooleanField
)
from knotis.utils.view import (
    format_currency,
    sanitize_input_html
)
from knotis.contrib.media.models import ImageInstance
from knotis.contrib.identity.models import (
    Identity,
    IdentityEstablishment,
    IdentityTypes
)
from knotis.contrib.inventory.models import Inventory
from knotis.contrib.endpoint.models import (
    EndpointTypes,
    Publish
)

from knotis.contrib.media.models import ImageInstance


class OfferStatus:  # REMOVE ME WHEN LEGACY CODE IS REMOVED FROM THE CODE BASE
    pass


class OfferTypes:
    NORMAL = 0
    PREMIUM = 1

    CHOICES = (
        (NORMAL, 'Normal'),
        (PREMIUM, 'Premium')
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


class OfferManager(QuickManager):
    def create(
        self,
        inventory=[],
        discount_factor=1.,
        *args,
        **kwargs
    ):
        offer = Offer(
            *args,
            **kwargs
        )
        offer.save()

        for i in inventory:
            price_discount = i.price * discount_factor
            OfferItem.objects.create(
                offer=offer,
                inventory=i,
                price_discount=price_discount
            )

        image = kwargs.get('image')
        if image:
            image.related_object_id = offer.id
            image.save()

        return offer

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
                    return offer.pub_time

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
                    return offer.end_time

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


class Offer(QuickModel):
    owner = QuickForeignKey(Identity)
    offer_type = QuickIntegerField(
        default=OfferTypes.NORMAL,
        choices=OfferTypes.CHOICES,
    )

    title = QuickCharField(
        max_length=140
    )
    description = QuickCharField(
        max_length=1024
    )
    restrictions = QuickCharField(
        max_length=1024
    )

    default_image = QuickForeignKey(ImageInstance)

    start_time = QuickDateTimeField()
    end_time = QuickDateTimeField()
    stock = QuickIntegerField(
        default=None
    )
    unlimited = QuickBooleanField(default=False)

    purchased = QuickIntegerField(default=0)
    redeemed = QuickIntegerField(default=0, blank=True, null=True)
    published = QuickBooleanField(default=False, db_index=True)
    active = QuickBooleanField(default=False, db_index=True)
    completed = QuickBooleanField(default=False, db_index=True)
    last_purchase = QuickDateTimeField(default=None)

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

        # Check whether offer should be completed on instansiation.
        # Could have no end date I guess so check for not None.
        if (
            self.end_time and self.end_time < datetime.datetime.utcnow()
        ) or (
            not self.unlimited and self.purchased >= self.stock
        ):
            self.complete()

    def _calculate_prices(self):
        if hasattr(self, '_price_retail') and hasattr(self, '_price_discount'):
            return

        offer_items = OfferItem.objects.filter(offer=self)
        price_retail = 0.0
        price_discount = 0.0
        for item in offer_items:
            stock = item.inventory.stock
            if stock and item.inventory.price:
                price_retail += stock * item.inventory.price
                price_discount += stock * item.price_discount

        self._price_retail = price_retail
        self._price_discount = price_discount

    def price_retail(self):
        self._calculate_prices()
        return self._price_retail

    def price_discount(self):
        self._calculate_prices()
        return self._price_discount

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
        pass

    def delete(self):
        self.deleted = True
        self.save()

    def available(self):
        now = datetime.datetime.utcnow()

        return self.active and \
            self.published and \
            self.start_time <= now and \
            self.end_time > now and \
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
        return format_currency(self.price_retail())

    def price_discount_formatted(self):
        return format_currency(self.price_discount())

    def savings(self):
        return format_currency(
            self.price_retail() - self.price_discount()
        )

    def savings_percent(self):
        return '%.0f' % round(
            (self.price_retail() - self.price_discount()) /
            self.price_retail() * 100, 0
        )

    def days_remaining(self):
        delta = self.end_time - datetime.datetime.utcnow()
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
        return (self.purchased * self.price_discount())

    def income_net_formatted(self):
        gross = self.income_gross()
        our_cut = gross * .03
        return format_currency(gross - our_cut)


class OfferItem(QuickModel):
    offer = QuickForeignKey(Offer)
    inventory = QuickForeignKey(Inventory)
    price_discount = QuickFloatField()


class OfferAvailabilityManager(QuickManager):
    def create(
        self,
        *args,
        **kwargs
    ):
        offer = kwargs.get('offer')

        if offer:
            kwargs['title'] = offer.title
            kwargs['stock'] = offer.stock
            kwargs['purchased'] = offer.purchased
            kwargs['default_image'] = offer.default_image

            offer_items = OfferItem.objects.filter(offer=offer)
            price = 0.
            for i in offer_items:
                price += i.price_discount

            kwargs['price'] = price

        identity = kwargs.get('identity')

        if identity:
            identity_profile_badge = ImageInstance.objects.get(
                related_object_id=identity.id,
                context='profile_badge',
                primary=True
            )
            kwargs['profile_badge'] = identity_profile_badge

        return super(OfferAvailabilityManager, self).create(
            *args,
            **kwargs
        )

    def update_denormalized_offer_fields(
        self,
        offer
    ):
        offers = self.objects.filter(offer=offer)
        for o in offers:
            o.title = offer.title
            o.stock = offer.stock
            o.purchased = offer.purchased
            o.default_image = offer.default_image
            o.save()

        return offers

    def update_denormalized_identity_fields(
        self,
        identity
    ):
        offers = self.objects.filter(identity=identity)
        identity_profile_badge = ImageInstance.objects.get(
            related_object_id=identity.id,
            context='profile_badge',
            primary=True
        )
        for o in offers:
            o.profile_badge = identity_profile_badge
            o.save()

        return offers

    def update_offer_price(
        self,
        offer
    ):
        offer_items = OfferItem.objects.filter(offer=offer)
        total_price = 0.
        for i in offer_items:
            total_price += i.price_discount

        offers = self.objects.filter(offer=offer)
        for o in offers:
            o.price = total_price
            o.save()


class OfferAvailability(QuickModel):
    """
    Represents an offer being redeemable by
    the related identity.

    Denormalized offer fields since this will
    most likely be a common call for rendering
    offers

    """
    offer = QuickForeignKey(Offer)
    identity = QuickForeignKey(Identity)
    title = QuickCharField(
        max_length=140
    )
    stock = QuickIntegerField()
    purchased = QuickIntegerField()
    default_image = QuickForeignKey(
        ImageInstance,
        related_name='offeravailability_offer_images'
    )

    profile_badge = QuickForeignKey(
        ImageInstance,
        related_name='offeravailability_badge_images'
    )

    price = QuickFloatField()
    available = QuickBooleanField(
        db_index=True,
        default=True
    )

    objects = OfferAvailabilityManager()


class OfferPublish(Publish):
    class Meta:
        proxy = True

    def _publish_establishment(
        self,
        establishment
    ):
        offer = self.subject
        OfferAvailability.objects.create(
            offer=offer,
            identity=establishment
        )
        offer.active = True
        offer.published = True
        offer.save()

    def publish(self):
        if self.endpoint.endpoint_type == EndpointTypes.IDENTITY:
            if (
                self.endpoint.identity.identity_type ==
                IdentityTypes.ESTABLISHMENT
            ):
                self._publish_establishment(self.endpoint.identity)

            elif (
                self.endpoint.identity.identity_type == IdentityTypes.BUSINESS
            ):
                # publish to all establishments.
                establishments = (
                    IdentityEstablishment.objects.get_establishments(
                        self.endpoint.identity
                    )
                )

                for e in establishments:
                    self._publish_establishment(e)

        else:
            raise NotImplementedError(''.join([
                'publish not implemented for endpoint type ',
                self.endpoint.endpoint_type,
                '.'
            ]))
