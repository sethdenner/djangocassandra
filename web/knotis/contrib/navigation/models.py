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

class NavigationTypes:
    LINK = 'link'
    HEADER = 'header'
    DIVIDER = 'divider'

    CHOICES = (
        (LINK, 'Link'),
        (HEADER, 'Header'),
        (DIVIDER, 'Divider'),
    )

class NavigationManager(QuickManager):
    def all_ordered(self):
        return sorted(
            self.all(),
            key=lambda item: item.order
        )

    def filter_ordered(
        self,
        *args,
        **kwargs
    ):
        return sorted(
            self.filter(
                *args,
                **kwargs
            ),
            key=lambda item: item.order
        )

class NavigationItem(QuickModel):
    item_type = QuickCharField(
        max_length=16,
        choices = NavigationTypes.CHOICES
    )
    title = QuickCharField(
        max_length=32
    )
    uri = QuickURLField(verify_exists=False)
    menu_name = QuickCharField(
        max_length=32
    )

    order = QuickIntegerField()
    parent = QuickForeignKey('self')

    objects = NavigationManager()

    def has_children(self):
        return self.navigationitem_set.count() > 0
