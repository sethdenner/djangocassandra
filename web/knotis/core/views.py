import copy

from django.conf import settings

from knotis.contrib.identity.models import IdentityIndividual
from knotis.contrib.identity.views import BusinessesView

from knotis.contrib.maps.views import GoogleMap

from knotis.views import ContextView


class IndexView(ContextView):
    template_name = 'knotis/layout/index.html'

    def process_context(self):
        request = self.request

        styles = self.context.get('styles', [])
        post_scripts = self.context.get('post_scripts', [])

        if request.user.is_authenticated():
            try:
                individual = IdentityIndividual.objects.get_individual(
                    request.user
                )

            except Exception:
                individual = None

            if (
                not individual or
                individual.name == IdentityIndividual.DEFAULT_NAME
            ):
                post_scripts.append('knotis/identity/js/first.js')
                styles.append('knotis/identity/css/first.css')

        maps = GoogleMap(settings.GOOGLE_MAPS_API_KEY)
        maps_scripts = maps.render_api_js()

        index_view_context = copy.copy(self.context)
        index_view_context.update({
            'styles': styles,
            'post_scripts': post_scripts,
            'maps_scripts': maps_scripts
        })

        businesses_view = BusinessesView()
        index_view_markup = businesses_view.render_template_fragment(
            index_view_context
        )

        local_context = copy.copy(self.context)
        local_context.update({
            'index_view_markup': index_view_markup
        })

        return local_context
