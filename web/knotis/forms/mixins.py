from django.template import (
    Context,
    RequestContext,
)

from django.template.loader import get_template
from django.utils.safestring import mark_safe


class TemplateFormMixin(object):
    template_name = None  # Must be defined by the derived class.

    def __init__(
        self,
        *args,
        **kwargs
    ):
        self.parameters = kwargs.pop('parameters', {})
        self.request = kwargs.pop('request', None)

        super(TemplateFormMixin, self).__init__(
            *args,
            **kwargs
        )

    def as_template(self):
        if not self.template_name:
            raise Exception('subclass must define template_name')

        self.parameters['form'] = self

        template = get_template(self.template_name)

        if isinstance(self.parameters, dict):
            if self.request:
                context = RequestContext(
                    self.request,
                    self.parameters
                )

            else:
                context = Context(self.parameters)

        elif isinstance(self.parameters, Context):
            context = self.parameters

        else:
            raise Exception('parameters must be Context or dict object')

        return mark_safe(
            template.render(context)
        )
