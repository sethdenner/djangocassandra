from django.forms import (
    ModelForm,
    CharField,
    HiddenInput
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


class LocationForm(ModelForm):
    class Meta:
        model = Location
        exclude = ('content_type')


class GeocompleteForm(LocationForm):
    class Meta(LocationForm.Meta):
        widgets = {
            'latitude': HiddenInput(),
            'longitude': HiddenInput()
        }

    address = CharField(
        max_length=256,
        label=''
    )

    related_id = CharField(
        max_length=36,
        label='',
        widget=HiddenInput()
    )

    def __init__(
        self,
        form_id='id-location-form',
        form_action='/api/v1/maps/location/',
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
            Field(
                'related_id',
                id='related-id-input'
            ),
            HTML('<div class="map_canvas"></div>'),
            FormActions(Submit('save', 'This Location Is Correct'))
        )
