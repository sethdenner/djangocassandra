from django.forms.widgets import SelectMultiple
from django.forms.fields import MultipleChoiceField


class ManyToManyWidget(SelectMultiple):
    pass


class ManyToManyFormField(MultipleChoiceField):
    widget = ManyToManyWidget

    def clean(self, value):
        return value
