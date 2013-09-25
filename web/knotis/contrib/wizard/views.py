import copy

from knotis.views import (
    AJAXFragmentView
)

class WizardStep(object):
    def __init__(self, action, element_id, params={}, *args, **kwargs):
        self.action = action
        self.element_id = element_id
        self.params = params

class WizardView(AJAXFragmentView):
    template_name = 'knotis/wizard/wizard.html'
    view_name = 'wizard'

    steps = []

    @classmethod
    def render_template_fragment(
            cls,
            context):
        #import ipdb;ipdb.set_trace()

        local_context = copy.copy(context)
        local_context.update({'steps':cls.steps})

        return super(WizardView, cls).render_template_fragment(local_context)
