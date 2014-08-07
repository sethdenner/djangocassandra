from knotis.contrib.layout.views import DefaultBaseView
from knotis.views import ModalView


class LocationModal(ModalView):
    template_name = 'knotis/location/location.html'
    view_name = 'location_form_view'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r'^location_form/$',
    ]
