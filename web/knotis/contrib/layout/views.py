from django.conf import settings
from django.shortcuts import render
from django.views.generic import View

from knotis.views import (
    FragmentView,
    AJAXFragmentView
)

from knotis.contrib.identity.models import IdentityIndividual
from knotis.contrib.maps.views import GoogleMap


class HeaderView(FragmentView):
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

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            HeaderView,
            cls
        ).render_template_fragment(context)


class IndexView(View):
    def get(
        self,
        request,
        *args,
        **kwargs
    ):
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

        context = {
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'maps_scripts': maps_scripts
        }

        return render(
            request,
            'knotis/layout/index.html',
            context
        )


class GridMixedView(FragmentView):
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


class GridSmallView(FragmentView):
    template_name = 'knotis/layout/grid_small.html'
    view_name = 'grid'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            GridSmallView,
            cls
        ).render_template_fragment(context)


class ItemSelectAction(object):
    def __init__(
        self,
        name,
        url,
        css_class,
        method='GET'
    ):
        self.name = name
        self.url = url,
        self.css_class = css_class
        self.method = method


class ItemSelectView(AJAXFragmentView):
    template_name = 'knotis/layout/item_select.html'
    view_name = 'item_select'

    def post(
        self,
        request
    ):
        pass

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        return super(
            ItemSelectView,
            cls
        ).render_template_fragment(context)
