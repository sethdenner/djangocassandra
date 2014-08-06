from django.template import Context
from django.forms import (
    IntegerField,
    CharField,
    EmailField,
    BooleanField,
    PasswordInput,
    HiddenInput,
    ValidationError
)

from knotis.forms import (
    TemplateForm,
    TemplateModelForm,
    TemplateFormMixin
)

class AdminQueryForm(TemplateForm):
    template_name = 'knotis/admintools/admin_query_form.html'

    range_start = IntegerField(
        label='Start',
        required = True,
        initial = 1,
    )
    range_end = IntegerField(
        label='Stop',
        required = True,
        initial = 20,
    )
    range_step = IntegerField(
        label='Step',
        required = True,
        initial = 20,
    )
    user_filter = CharField(
        label='Filter',
        max_length = 254,
        required = True,
        initial = ' ',
    )
    target_uri = CharField(
        label='',
        max_length = 254,
        required = True,
        initial = 'query/',
    )
