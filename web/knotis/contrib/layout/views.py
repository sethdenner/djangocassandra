import copy

from knotis.views import (
    FragmentView,
    ModalView,
    EmbeddedView
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


class ToTopButton(FragmentView):
    template_name = 'knotis/layout/to_top.html'
    view_name = 'to_top_button'


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



class DefaultBaseView(EmbeddedView):
    template_name = 'knotis/layout/default_base.html'
    template_placeholders = ['content', 'modal_content']

    def process_context(self):
        current_identity_pk = self.context.get('current_identity_pk')
        if not current_identity_pk:
            current_identity_pk = self.request.session.get('current_identity')
            self.context['current_identity_pk'] = current_identity_pk

        return self.context


class UnderConstructionView(ModalView):
    url_patterns = [
        r'^underconstruction/$',
    ]

    template_name = 'knotis/layout/under_construction.html'
    view_name = 'under_construction'
    default_parent_view_class = DefaultBaseView
    