from django.forms import (
    Form,
    CharField
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Submit
)
from crispy_forms.bootstrap import FieldWithButtons


class SearchForm(Form):
    q = CharField(
        label='',
        required=False
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(SearchForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-searchForm'
        self.helper.form_class = 'navbar-form'
        self.helper.form_method = 'get'
        self.helper.form_action = '/search/'
        self.helper.layout = Layout(
            FieldWithButtons(
                Field(
                    'q',
                    id='q',
                    css_class='span4',
                    placeholder='Search businesses and offers around you',
                ),
                Submit(
                    'search',
                    '',
                    css_class='btn-search'
                )
            )
        )
