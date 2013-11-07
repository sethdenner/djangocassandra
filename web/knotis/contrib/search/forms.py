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
    search_input = CharField(
        label=''
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
        self.helper.form_action = 'search_results'
        self.helper.layout = Layout(
            FieldWithButtons(
                Field(
                    'search_input',
                    id='search-input',
                    css_class='span4',
                    placeholder='Search businesses and offers around you'
                ),
                Submit(
                    'search',
                    'Search'
                )
            )
        )
