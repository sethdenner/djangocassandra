from django.forms import (
    ModelForm,
    CharField,
    IntegerField,
    HiddenInput
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    HTML,
    Div,
    Field,
    ButtonHolder,
    Submit
)

from models import (
    Location,
    LocationItem
)


class LocationForm(ModelForm):
    class Meta:
        model = Location
        widgets = {
            'latitude': HiddenInput(),
            'longitude': HiddenInput(),
            'short_name': HiddenInput(),
            'long_name': HiddenInput()
        }

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(LocationForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-location-form'
        self.helper.form_method = 'post'
        self.helper.form_action = '/api/v1/location/location/'
        self.helper.layout = Layout(
            Field('latitude', id='latitude-input'),
            Field('longitude', id='longitude-input'),
            Field('short_name', id='short-name-input'),
            Field('long_name', id='long-name-input')
        )
