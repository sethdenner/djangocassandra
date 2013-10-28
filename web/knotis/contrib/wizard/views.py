import copy

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.core.urlresolvers import reverse

from knotis.views import (
    FragmentView,
    AJAXFragmentView
)

from knotis.contrib.identity.models import Identity

from models import (
    WizardStep,
    WizardProgress
)


class WizardStepView(AJAXFragmentView):
    wizard_name = None

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(WizardStepView, self).__init__(
            *args,
            **kwargs
        )

        if not self.wizard_name:
            raise Exception(''.join([
                'WizardStepView <',
                self.__class__.__name__,
                '> did not define a wizard_name.'
            ]))

        action = reverse(self.view_name)
        self.step = WizardStep.objects.get(
            action=action,
            wizard_name=self.wizard_name
        )

    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):
        try:
            self.current_identity = Identity.objects.get(
                pk=request.session.get('current_identity_id')
            )

        except:
            self.current_identity = None

        return super(WizardStepView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def build_query_string(self):
        '''
        Override this in subclass for
        generating the query string
        for this wizard instance
        '''
        return ''

    def advance(
        self,
        lookup_query_string=None
    ):
        query_string = self.build_query_string()

        if None == lookup_query_string:
            lookup_query_string = query_string

        progress = WizardProgress.objects.get(
            identity=self.current_identity,
            wizard_name=self.wizard_name,
            query_string=lookup_query_string,
            completed=False
        )

        if query_string != progress.query_string:
            progress.query_string = query_string

        progress.step(self.step.get_next_step())


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
