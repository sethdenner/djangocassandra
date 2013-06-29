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

    CHOICES = (
        (USD, 'United States Dollars ($)')
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


class Product(QuickModel):
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
    public = QuickBooleanField(default=True)
    sku = QuickCharField(
        max_length=32
    )

    currency = ProductCurrencyManager()
