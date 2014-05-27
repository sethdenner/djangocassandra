from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickBooleanField,
    QuickCharField,
    QuickForeignKey
)
from knotis.contrib.media.models import (
    Image
)
#from knotis.contrib.offer.models import (
#    Offer
#)


class ProductTypes:
    PHYSICAL = 'physical'
    EVENT = 'event'
    SERVICE = 'service'
    CURRENCY = 'currency'
    DIGITAL = 'digital'
    CREDIT = 'credit'

    CHOICES = (
        (PHYSICAL, 'Physical'),
        (EVENT, 'Event'),
        (SERVICE, 'Service'),
        (CURRENCY, 'Currency'),
        (DIGITAL, 'Digital'),
        (CREDIT, 'Credit')
    )


class CurrencyCodes:
    USD = 'usd'
    KNOTIS_POINTS = 'kno'

    CHOICES = (
        (USD, 'United States Dollars ($)'),
        (KNOTIS_POINTS, 'Knotis Reward Points (k)'),
    )


class ProductCurrencyManager(QuickManager):
    def get(
        self,
        currency_code
    ):
        return Product.objects.get(
            product_type=ProductTypes.CURRENCY,
            sku=currency_code
        )


class ProductManager(QuickManager):
    @staticmethod
    def _generate_credit_sku(
        price,
        value,
        currency_code,
    ):
        return '_'.join([
            Product.CREDIT_SKU_PREFIX,
            currency_code,
            ('%.2f' % price).rstrip('00').rstrip('.'),
            ('%.2f' % value).rstrip('00').rstrip('.')
        ])

    @staticmethod
    def _generate_physical_sku(title):
        return '_'.join([
            Product.PHYSICAL_SKU_PREFIX,
            title.lower().replace(' ', '_').replace('\'', '')
        ])

    def get_or_create_credit(
        self,
        price,
        value,
        currency_code=CurrencyCodes.USD,
    ):
        sku = self._generate_credit_sku(
            price,
            value,
            currency_code,
        )

        try:
            product = self.get(
                product_type=ProductTypes.CREDIT,
                sku=sku
            )

        except Product.DoesNotExist:
            product = None

        if not product:
            product = self.create(
                product_type=ProductTypes.CREDIT,
                title=''.join([
                    ('%.2f' % price).rstrip('00').rstrip('.'),
                    ' for ',
                    ('%.2f' % value).rstrip('00').rstrip('.')
                ]),
                description=''.join([
                    '$',
                    ('%.2f' % value).rstrip('00').rstrip('.'),
                    'worth of credit'
                ]),
                primary_image=None,
                public=False,
                sku=self._generate_credit_sku(
                    price,
                    value,
                    currency_code
                )
            )

        return product

    def get_or_create_physical(
        self,
        title
    ):
        sku = self._generate_physical_sku(
            title
        )

        try:
            product = self.get(
                product_type=ProductTypes.PHYSICAL,
                sku=sku
            )

        except Product.DoesNotExist:
            product = None

        if not product:
            product = self.create(
                product_type=ProductTypes.PHYSICAL,
                title=title,
                public=False,
                sku=self._generate_physical_sku(
                    title
                )
            )

        return product


class Product(QuickModel):
    CREDIT_SKU_PREFIX = '_'.join([
        'knotis',
        ProductTypes.CREDIT,
        'sku'
    ])
    PHYSICAL_SKU_PREFIX = '_'.join([
        'knotis',
        ProductTypes.PHYSICAL,
        'sku'
    ])

    product_type = QuickCharField(
        max_length=16,
        db_index=True,
        choices=ProductTypes.CHOICES
    )
    title = QuickCharField(
        max_length=140,
        db_index=True
    )
    description = QuickCharField(
        max_length=140
    )
    primary_image = QuickForeignKey(Image)
    public = QuickBooleanField(
        db_index=True,
        default=True
    )
    sku = QuickCharField(
        db_index=True,
        max_length=32
    )

    currency = ProductCurrencyManager()
    objects = ProductManager()
