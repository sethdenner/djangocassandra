from django.forms import Form
from django.template import (
    Context,
    Template
)
from django.template.loader import get_template
from django.utils.safestring import mark_safe

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

        self.parameters.update({
            'form': self,
        })

        template = Template(
            get_template(self.template_name)
        )
        context = Context(self.parameters)
        return mark_safe(
            template.render(context)
        )
