from knotis.contrib.quick.fields import (
    QuickForeignKey,
    QuickCharField
)
from knotis.contrib.quick.models import (
    QuickModel
)
from knotis.contrib.identity.models import Identity

class StripeCustomer(QuickModel):
    identity = QuickForeignKey(Identity)
    stripe_id = QuickCharField(max_length=256)
    description = QuickCharField(max_length=1024)
