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
    action = QuickURLField()
    order = QuickIntegerField()
    wizard_name = QuickCharField(
        max_length=16,
        db_index=True
    )

    objects = WizardStepManager()


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

    def steps(self):
        return WizardStep.objects.get_wizard_steps(self.wizard_name)

    def next(self):
        steps = self.steps()

        next_step = False
        updated = False
        for s in steps:
            if next_step:
                self.current_step = s
                self.save()
                updated = True
                break

            elif self.current_step_id == s.id:
                next_step = True

        if not updated:
            self.completed = True
            self.save()
