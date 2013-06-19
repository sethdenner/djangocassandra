from django.conf import settings
from django.views.generic import View
from django.shortcuts import render

from knotis.views.mixins import RenderTemplateFragmentMixin

from knotis.contrib.identity.models import IdentityIndividual
from knotis.contrib.maps.views import GoogleMap


class HeaderView(View, RenderTemplateFragmentMixin):
    template_name = 'knotis/layout/header.html'
    view_name = 'header'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return render(
            request,
            self.template_name,
            {}
        )


class IndexView(View):
    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        styles = [
            'layout/css/header.css',
            'layout/css/grid.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css'
        ]

        pre_scripts = []

        post_scripts = [
            'geocomplete/jquery.geocomplete.min.js',
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'layout/js/header.js',
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

        context = {
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'maps_scripts': maps_scripts
        }

        return render(
            request,
            'layout/index.html',
            context
        )


class GridMixedView(View, RenderTemplateFragmentMixin):
    template_name = 'knotis/layout/grid_mixed.html'
    view_name = 'grid_mixed'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            GridMixedView,
            cls
        ).render_template_fragment(context)
