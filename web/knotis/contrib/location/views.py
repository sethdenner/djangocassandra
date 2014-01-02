import copy

from knotis.contrib.maps.forms import GeocompleteForm
from knotis.views import FragmentView

class LocationFormView(FragmentView):
    template_name = 'knotis/location/location.html'
    view_name = 'location_form_view'
    
    def process_context(self):
        local_context = copy.copy(self.context)
        local_context.update({
            'location_form': GeocompleteForm()
        })

        return local_context


