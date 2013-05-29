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
    Hidden,
    ButtonHolder,
    Submit
)

from models import (
    Identity,
    IdentityTypes
)


class IdentityFirstForm(ModelForm):
    class Meta:
        model = Identity
        fields = [
            'name',
            'identity_type'
        ]

    name = CharField(
        max_length=80,
        label=''
    )

    identity_type = IntegerField(
        initial=IdentityTypes.INDIVIDUAL,
        widget=HiddenInput
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(IdentityFirstForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-identity-form'
        self.helper.form_method = 'post'
        self.helper.form_action = '/api/v1/identity/identity/'
        self.helper.layout = Layout(
            Div(
                HTML(
                    '<p>First thing\'s first. Tell us '
                    'your name so we can personalize '
                    'your Knotis account.</p>'
                ),
                Field(
                    'name',
                    id='name-input',
                    placeholder='Your Name',
                ),
                Field(
                    'identity_type',
                    id='identity-type-input',
                ),
                HTML(
                    '<span class="help-block">This is '
                    'the name that will be displayed '
                    'publicly in Knotis services.</span>'
                ),
                css_class='modal-body'
            ),
            ButtonHolder(
                Submit(
                    'save-identity',
                    'Continue'
                ),
                css_class='modal-footer'
            )
        )
