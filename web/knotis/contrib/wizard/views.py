import copy

from django.utils.log import logging
logger = logging.getLogger(__name__)
from knotis.views import (
    FragmentView
)

from knotis.contrib.identity.models import Identity

from models import (
    WizardStep,
    WizardProgress
)


class WizardView(FragmentView):
    template_name = 'knotis/wizard/wizard.html'
    view_name = 'wizard'
    wizard_name = None

    steps = []

    def __init__(
        self,
        *args,
        **kwargs
    ):
        if not self.wizard_name:
            raise Exception(''.join([
                'WizardView <',
                self.__class__.__name__,
                '> did not define a wizard_name.'
            ]))

        self.steps = WizardStep.objects.get_wizard_steps(self.wizard_name)
        if not self.steps:
            raise Exception(''.join([
                'No WizardStep`s for wizard_name: ',
                self.wizard_name
            ]))

        super(WizardView, self).__init__(
            *args,
            **kwargs
        )

    def process_context(self):
        local_context = copy.copy(self.context)

        request = local_context.get('request')
        if request:
            current_identity_id = request.session.get('current_identity_id')
            try:
                current_identity = Identity.objects.get(pk=current_identity_id)

            except:
                current_identity = None
                logger.exception(''.join([
                    'Could not get current identity with pk=',
                    current_identity_id
                ]))

            if current_identity:
                try:
                    progress = WizardProgress.objects.get(
                        identity=current_identity,
                        wizard_name=self.wizard_name,
                        query_string=request.META.get('QUERY_STRING', ''),
                        completed=False
                    )

                except WizardProgress.DoesNotExist:
                    progress = WizardProgress.objects.create(
                        identity=current_identity,
                        wizard_name=self.wizard_name,
                        current_step=self.steps[0]
                    )

                except:
                    progress = None
                    logger.exception('could not get progress object')

                if progress:
                    local_context['progress'] = progress

        local_context.update({
            'steps': self.steps,
            'wizard_name': self.wizard_name
        })

        return local_context
