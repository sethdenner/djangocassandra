from django.template import (
    RequestContext,
    Context
)

from knotis.contrib.layout.views import (
    ItemSelectView,
    ItemSelectRow,
    ItemSelectAction
)


class LocationSelectView(ItemSelectView):
    view_name = 'location_select'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        items = context.get('location_select_items')
        if not items:
            return super(
                LocationSelectView,
                cls
            ).render_template_fragment(Context())

        rows = [
            ItemSelectRow(
                location,
                title=location.address
            ) for location in items
        ]
        actions = [
            ItemSelectAction(
                'Edit Location',
                '#edit-location'
            )
        ]

        request = context.get('request')
        local_context = RequestContext(request)
        local_context.update({
            'rows': rows,
            'actions': actions,
            'item_select_scripts': None,
            'select_multiple': True,
            'render_images': False
        })

        return super(
            LocationSelectView,
            cls
        ).render_template_fragment(local_context)
