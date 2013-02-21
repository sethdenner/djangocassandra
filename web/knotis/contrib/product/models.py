from knotis.contrib.quick.models import (
    QuickModel,
    QuickBooleanField,
    QuickCharField,
    QuickForigenKey
)
from knotis.contrib.media.models import (
    Image
)


class Product(QuickModel):
    title = QuickCharField(
        max_length=140,
        db_index=True
    )
    description = QuickCharField(
        max_length=140
    )
    primary_image = QuickForigenKey(Image)
    public = QuickBooleanField()
    sku = QuickCharField(
        max_length=32
    )
