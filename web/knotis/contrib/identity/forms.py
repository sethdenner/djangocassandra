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
            'id',
            'name',
            'identity_type'
        ]

    id = CharField(
        max_length=36,
        initial=None,
        label='',
        required=False,
        widget=HiddenInput()
    )

    name = CharField(
        max_length=80,
        label=''
    )

    subject_id = CharField(
        max_length=36,
        label='',
        required=False,
        widget=HiddenInput()
    )

    def __init__(
        self,
        form_id='id-identity-form',
        form_method='post',
        form_action='/api/v1/identity/identity/',
        description_text=None,
        placeholder_text=None,
        help_text=None,
        *args,
        **kwargs
    ):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        if instance:
            if instance.is_name_default():
                initial.update({'name': ''})
                kwargs['initial'] = initial

        super(IdentitySimpleForm, self).__init__(
            *args,
            **kwargs
        )

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
                    'id',
                    id='id-input'
                ),
                Field(
                    'name',
                    id='name-input',
                    placeholder=placeholder_text
                ),
                Field(
                    'identity_type',
                    id='identity-type-input'
                ),
                Field(
                    'subject_id',
                    id='identity-subject-input'
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


class IdentityIndividualSimpleForm(IdentitySimpleForm):
    identity_type = IntegerField(
        initial=IdentityTypes.INDIVIDUAL,
        widget=HiddenInput()
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(IdentityIndividualSimpleForm, self).__init__(
            placeholder_text='Your Name',
            *args,
            **kwargs
        )


class IdentityBusinessSimpleForm(IdentitySimpleForm):
    identity_type = IntegerField(
        initial=IdentityTypes.BUSINESS,
        widget=HiddenInput()
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(IdentityBusinessSimpleForm, self).__init__(
            placeholder_text='Business Name',
            *args,
            **kwargs
        )


class IdentityEstablishmentSimpleForm(IdentitySimpleForm):
    identity_type = IntegerField(
        initial=IdentityTypes.ESTABLISHMENT,
        widget=HiddenInput()
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(IdentityEstablishmentSimpleForm, self).__init__(
            placeholder_text='Establishment Name',
            *args,
            **kwargs
        )
