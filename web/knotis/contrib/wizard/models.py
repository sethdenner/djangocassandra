from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickForeignKey,
    QuickURLField,
    QuickIntegerField,
    QuickBooleanField
)

from knotis.contrib.identity.models import Identity


class WizardStepManager(QuickManager):
    def get_wizard_steps(
        self,
        wizard_name
    ):
        return sorted(
            self.filter(wizard_name=wizard_name),
            key=lambda item: item.order
        )


class WizardStep(QuickModel):
    action = QuickURLField(
        db_index=True
    )
    order = QuickIntegerField()
    wizard_name = QuickCharField(
        max_length=16,
        db_index=True
    )

    objects = WizardStepManager()

    def steps(self):
        return WizardStep.objects.get_wizard_steps(self.wizard_name)

    def get_next_step(
        self
    ):
        steps = self.steps()

        next_step = None
        found_current = False
        for step in steps:
            if found_current:
                next_step = step
                break

            if self.id == step.id:
                found_current = True

        return next_step


class WizardProgress(QuickModel):
    identity = QuickForeignKey(Identity)
    wizard_name = QuickCharField(
        max_length=16,
        db_index=True
    )
    query_string = QuickCharField(
        max_length=1024,
        db_index=True,
        default=''
    )

    current_step = QuickForeignKey(WizardStep)
    completed = QuickBooleanField(
        default=False,
        db_index=True
    )

    def step(
        self,
        step,
        allow_completed=False
    ):
        if step.wizard_name != self.wizard_name:
            raise Exception(''.join([
                'step: <',
                step.id,
                '> does not belong to wizard "',
                self.wizard_name,
                '".'
            ]))

        if allow_completed or step.order > self.current_step.order:
            self.current_step = step
            self.save()

        return self.current_step

    def get_next_step(self):
        return self.current_step.get_next_step()

    def next(self):
        next_step = self.get_next_step()
        if not next_step:
            self.completed = True
            self.save()
            return

        self.step(next_step)
