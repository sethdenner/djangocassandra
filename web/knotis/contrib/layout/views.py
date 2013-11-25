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
        data={},
        method='get'
    ):
        self.title = title
        self.href = href
        self.data = data
        self.method = method.lower()


class ActionButton(FragmentView):
    template_name = 'knotis/layout/action_button.html'
    view_name = 'action_button'

    def process_context(self):
        self.context = copy.copy(self.context)

        self.context.update({
            'actions': self.actions(),
            'css_class': 'btn-knotis-action'
        })

        return self.context

    def actions(self):
        '''
        Override this in subclass. Should return an array of ButtonAction
        '''
        return []
