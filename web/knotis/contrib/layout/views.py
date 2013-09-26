import copy

from django.conf import settings

from knotis.views import (
    FragmentView,
    ContextView
)

from knotis.contrib.identity.models import IdentityIndividual
from knotis.contrib.maps.views import GoogleMap


class HeaderView(FragmentView):
    template_name = 'knotis/layout/header.html'
    view_name = 'header'


class IndexView(ContextView):
    template_name = 'knotis/layout/index.html'

    def process_context(self):
        request = self.request
        styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'knotis/identity/css/switcher.css'
        ]

        pre_scripts = []

        post_scripts = [
            'geocomplete/jquery.geocomplete.min.js',
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'navigation/js/navigation.js'
        ]

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

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'maps_scripts': maps_scripts
        })

        return local_context


class GridMixedView(FragmentView):
    template_name = 'knotis/layout/grid_mixed.html'
    view_name = 'grid_mixed'


class GridSmallView(FragmentView):
    template_name = 'knotis/layout/grid_small.html'
    view_name = 'grid'
