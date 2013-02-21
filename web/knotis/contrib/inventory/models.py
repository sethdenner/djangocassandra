from knotis.contrib.quick.models import (
    QuickModel,
    QuickForeignKey,
    QuickIntegerField
)

from knotis.contrib.identity.models import (
    Identity
)

from kontis.contrib.product.models import (
    Product
)


class Inventory(QuickModel):
    product = QuickForeignKey(Product)
    owner = QuickForeignKey(Identity)
    supplier = QuickForeignKey(Identity)
    stock = QuickIntegerField()
