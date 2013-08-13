from django.db.models import Manager

from knotis.contrib.quick.models import (
    QuickModel
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


class NavigationManager(Manager):
    def all_ordered(self):
        return sorted(
            super(NavigationManager, self).all(),
            key=lambda item: item.order
        )

    def filter_ordered(
        self,
        *args,
        **kwargs
    ):
        return sorted(
            super(NavigationManager, self).filter(
                *args,
                **kwargs
            ),
            key=lambda item: item.order
        )


class NavigationItem(QuickModel):
    item_type = QuickCharField(
        max_length=16,
        choices=NavigationTypes.CHOICES
    )
    title = QuickCharField(
        max_length=32
    )
    uri = QuickURLField()
    menu_name = QuickCharField(
        max_length=32
    )

    order = QuickIntegerField()
    parent = QuickForeignKey(
        'self',
        related_name='children'
    )

    objects = NavigationManager()

    def has_children(self):
        return self.children.count() > 0
