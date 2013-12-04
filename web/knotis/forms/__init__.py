from django.forms import (
    Form,
    ModelForm as DjangoModelForm
)
from django.forms.models import model_to_dict


from fields import (
    UUIDField
)
from widgets import (
    ItemSelectWidget,
    ItemSelectRow,
    ItemSelectAction
)

from mixins import TemplateFormMixin


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


class TemplateForm(TemplateFormMixin, Form):
    pass


class TemplateModelForm(TemplateFormMixin, ModelForm):
    pass
