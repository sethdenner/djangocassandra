from knotis.contrib.quick.models import (
    QuickModel
)
from knotis.contrib.quick.fields import (
    QuickForeignKey,
    QuickIntegerField,
    QuickFloatField
)
from knotis.contrib.identity.models import (
    Identity
)

from knotis.contrib.product.models import (
    Product
)


class Inventory(QuickModel):
    product = QuickForeignKey(Product)
    owner = QuickForeignKey(Identity, related_name='identity_owner')
    supplier = QuickForeignKey(Identity, related_name='identity_supplier')
    stock = QuickIntegerField()
    retail_price = QuickFloatField()
