from knotis.contrib.layout.views import ItemSelectView


class LocationSelectView(ItemSelectView):
    view_name = 'location_select'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            LocationSelectView,
            cls
        ).render_template_fragment(context)
