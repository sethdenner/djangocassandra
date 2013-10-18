from django.forms import (
    Form,
    ModelForm as DjangoModelForm
)
from django.forms.models import model_to_dict

from django.template import Context
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


class ModelForm(DjangoModelForm):
    def __init__(
        self,
        data=None,
        instance=None,
        *args,
        **kwargs
    ):
        if instance and data:
            fields = getattr(self.Meta, 'fields', None)
            exclude = getattr(self.Meta, 'exclude', None)
            instance_data = model_to_dict(
                instance,
                fields,
                exclude
            )
            data_dict = dict(
                (
                    key,
                    value
                ) for key, value in data.iteritems()
            )

            instance_data.update(data_dict)
            data = instance_data

        super(ModelForm, self).__init__(
            data=data,
            instance=instance,
            *args,
            **kwargs
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
