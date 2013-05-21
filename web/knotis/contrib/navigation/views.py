from django.views.generic import View
from django.shortcuts import render

from knotis.views.mixins import RenderTemplateFragmentMixin

from models import (
    NavigationItem,
    NavigationTypes
)

class NavigationTopView(View, RenderTemplateFragmentMixin):
    template_name = 'navigation/nav_top.html'
    view_name = 'nav_top'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        context['navigation_items'] = NavigationItem.objects.filter(
            menu_name='nav_top'
        )

        return super(
            NavigationTopView,
            cls
        ).render_template_fragment(context)


class NavigationSideView(View, RenderTemplateFragmentMixin):
    template_name = 'navigation/nav_side.html'
    view_name = 'nav_side'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):

        context['NAVIGATION_TYPES'] = NavigationTypes
        context['navigation_items'] = NavigationItem.objects.filter_ordered(
            menu_name='default'
        )

        return super(
            NavigationSideView,
            cls
        ).render_template_fragment(context)
