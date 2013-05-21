from django.views.generic import View
from django.shortcuts import render

from knotis.views.mixins import RenderTemplateFragmentMixin

class HeaderView(View, RenderTemplateFragmentMixin):
    template_name = 'layout/header.html'
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
        context = {
            'styles': [
                'layout/css/header.css',
                'layout/css/grid.css',
                'navigation/css/nav_top.css',
                'navigation/css/nav_side.css'
            ],
            'scripts': [
                'navigation/js/navigation.js'
            ]
        }

        return render(
            request,
            'layout/index.html',
            context
        )

class GridMixedView(View, RenderTemplateFragmentMixin):
    template_name = 'layout/grid_mixed.html'
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


