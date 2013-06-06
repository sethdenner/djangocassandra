from django.forms import (
    ModelForm,
    CharField,
    HiddenInput,
    TextInput
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Submit,
    HTML
)
from crispy_forms.bootstrap import (
    FieldWithButtons,
    StrictButton,
    FormActions
)

from models import Location


class GeocompleteForm(ModelForm):
    class Meta:
        model = Location
        widgets = {
            'latitude': HiddenInput(),
            'longitude': HiddenInput()
        }

    address = CharField(
        max_length=256,
        label=''
    )

    def __init__(
        self,
        form_id='id-location-form',
        form_action='/api/v1/location/location/',
        *args,
        **kwargs
    ):
        super(GeocompleteForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = form_id
        self.helper.form_method = 'post'
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            FieldWithButtons(
                'address',
                StrictButton('Search'),
                id='address-input',
                placeholder='Enter An Address',
                data_geo='address_formatted'
            ),
            Field(
                'latitude',
                id='latitude-input',
                data_geo='lat'
            ),
            Field(
                'longitude',
                id='longitude-input',
                data_geo='lng'
            ),
            HTML('<div class="map_canvas"></div>'),
            FormActions(Submit('save', 'This Location Is Correct'))
        )
