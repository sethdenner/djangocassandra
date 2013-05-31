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
    Identity,
    IdentityTypes
)


class IdentityForm(ModelForm):
    class Meta:
        model = Identity


class IdentitySimpleForm(IdentityForm):
    class Meta(IdentityForm.Meta):
        fields = [
            'name',
            'identity_type'
        ]

    name = CharField(
        max_length=80,
        label=''
    )

    def __init__(
        self,
        form_id='id-identity-form',
        form_method='post',
        form_action='/api/v1/identity/identity/',
        identity_type=None,
        description_text=None,
        help_text=None,
        *args,
        **kwargs
    ):
        super(IdentitySimpleForm, self).__init__(
            *args,
            **kwargs
        )

        if identity_type:
            self.fields['identity_type'].initial = identity_type
            self.fields['identity_type'].widget = HiddenInput()

            if identity_type == IdentityTypes.INDIVIDUAL:
                placeholder_name = 'Your Name'

            elif identity_type == IdentityTypes.BUSINESS:
                placeholder_name = 'Business Name'

            elif identity_type == IdentityTypes.ESTABLISHMENT:
                placeholder_name = 'Establishment Name'

            else:
                placeholder_name = ''

        else:
            placeholder_name = ''

        self.helper = FormHelper()
        self.helper.form_id = form_id
        self.helper.form_method = form_method
        self.helper.form_action = form_action

        if description_text:
            element_description_text = HTML(
                ''.join([
                    '<p>',
                    description_text,
                    '</p>'
                ])
            )

        else:
            element_description_text = None

        if help_text:
            element_help_text = HTML(
                ''.join([
                    '<span class="help-block">',
                    help_text,
                    '</span>'
                ])
            )

        else:
            element_help_text = None

        self.helper.layout = Layout(
            Div(
                element_description_text,
                Field(
                    'name',
                    id='name-input',
                    placeholder=placeholder_name,
                ),
                Field(
                    'identity_type',
                    id='identity-type-input',
                ),
                element_help_text,
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
