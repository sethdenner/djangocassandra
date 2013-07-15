from django.template import Context
from django.template.loader import get_template
from django.conf import settings

from knotis.contrib.layout.views import ItemSelectView


class LocationSelectView(ItemSelectView):
    template_name = 'knotis/maps/location_select.html'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            LocationSelectView,
            cls
        ).render_template_fragment(context)


class GoogleMap(object):
    def __init__(
        self,
        key
    ):
        self.key = key

    def render_api_js(self):
        google_maps_api_script_html = get_template(
            'google_maps_api.html'
        )
        context = Context({
            'key': self.key
        })
        return google_maps_api_script_html.render(context)


class OfferMap(GoogleMap):
    def __init__(
        self,
        key,
        offers,
        center=(
            47.602227802480606,
            - 122.30203628540039
        ),
        map_zoom=15,
        map_type='ROADMAP',
        map_element_id='map_canvas',
        *args,
        **kwargs
    ):
        super(OfferMap, self).__init__(
            key,
            *args,
            **kwargs
        )

        self.offers = offers
        self.center = center
        self.map_zoom = map_zoom
        self.map_type = map_type
        self.map_element_id = map_element_id

    def center_lat(self):
        return self.center[0]

    def center_lon(self):
        return self.center[1]

    def _get_map_parameters_dict(self):
        return {
            'offers': self.offers,
            'center_lat': self.center_lat(),
            'center_lon': self.center_lon(),
            'map_zoom': self.map_zoom,
            'map_type': self.map_type,
            'map_element_id': self.map_element_id,
            'STATIC_URL': settings.STATIC_URL
        }

    def render(self):
        map_script_html = get_template('knotis_map_offer.html')
        context = Context(self._get_map_parameters_dict())
        return map_script_html.render(context)
