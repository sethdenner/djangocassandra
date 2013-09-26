import copy

from knotis.views import (
    FragmentView
)


class WizardStep(object):
    def __init__(self, action, element_id, params={}, *args, **kwargs):
        self.action = action
        self.element_id = element_id
        self.params = params


class WizardView(FragmentView):
    template_name = 'knotis/wizard/wizard.html'
    view_name = 'wizard'

    steps = []

    def process_context(self):
        local_context = copy.copy(self.context)
        local_context.update({'steps': self.steps})

        return local_context
