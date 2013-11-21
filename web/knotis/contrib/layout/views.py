import copy

from knotis.views import (
    FragmentView
)


class HeaderView(FragmentView):
    template_name = 'knotis/layout/header.html'
    view_name = 'header'


class GridMixedView(FragmentView):
    template_name = 'knotis/layout/grid_mixed.html'
    view_name = 'grid_mixed'


class GridSmallView(FragmentView):
    template_name = 'knotis/layout/grid_small.html'
    view_name = 'grid'


class ButtonAction(object):
    def __init__(
        self,
        title,
        href,
        data={}
    ):
        self.title = title
        self.href = href
        self.data = data


class ActionButton(FragmentView):
    template_name = 'knotis/layout/action_button.html'
    view_name = 'action_button'

    def process_context(self):
        local_context = copy.copy(self.context)

        local_context.update({
            'css_class': 'btn-primary',
            'primary_action': ButtonAction(
                'Action',
                '#'
            ),
            'actions': []
        })

        return local_context
