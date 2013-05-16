from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickForeignKey,
    QuickCharField,
    QuickURLField,
    QuickIntegerField
)

class NavigationItem(QuickModel):
    title = QuickCharField(
        max_length=32
    )
    uri = QuickURLField()
    menu_name = QuickCharField(
        max_length=32
    )

    order = QuickIntegerField()
    parent = QuickForeignKey('self')
