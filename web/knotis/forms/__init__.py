from django.forms import Form
from django.template import (
    Context,
    Template
)
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from fields import (
    UUIDField
)
from widgets import (
    ItemSelectWidget,
    ItemSelectRow,
    ItemSelectAction
)


class TemplateForm(Form):
    template_name = None  # Must be defined by the derived class.

    def __init__(
        self,
        parameters={},
        *args,
        **kwargs
    ):
        self.parameters = parameters

        super(TemplateForm, self).__init__(
            *args,
            **kwargs
        )

    def as_template(self):
        if not self.template_name:
            raise Exception('subclass must define template_name')

        self.parameters['form'] = self

        template = get_template(self.template_name)

        if isinstance(self.parameters, dict):
            context = Context(self.parameters)

        elif isinstance(self.parameters, Context):
            context = self.parameters

        else:
            raise Exception('parameters must be Context or dict object')

        return mark_safe(
            template.render(context)
        )
