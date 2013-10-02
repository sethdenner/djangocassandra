import copy

from knotis.contrib.layout.views import (
    ItemSelectView,
    ItemSelectRow,
    ItemSelectAction
)


class LocationSelectView(ItemSelectView):
    view_name = 'location_select'
    field_name = 'location_id'

    def process_context(self):
        items = self.context.get('location_select_items')
        if not items:
            return self.context

        rows = [
            ItemSelectRow(
                location,
                title=location.address,
                checked=True
            ) for location in items
        ]
        actions = [
            ItemSelectAction(
                'Edit Location',
                '#edit-location'
            )
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'rows': rows,
            'actions': actions,
            'item_select_scripts': None,
            'select_multiple': True,
            'render_images': False
        })

        return local_context
