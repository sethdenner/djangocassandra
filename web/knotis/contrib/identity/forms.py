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
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment,
    IdentityTypes
)


class IdentityForm(ModelForm):
    class Meta:
        model = Identity
        exclude = ('content_type')


class IdentityIndividualForm(IdentityForm):
    class Meta(IdentityForm.Meta):
        model = IdentityIndividual


class IdentityBusinessForm(IdentityForm):
    class Meta(IdentityForm.Meta):
        model = IdentityBusiness


class IdentityEstablishmentForm(IdentityForm):
    class Meta(IdentityForm.Meta):
        model = IdentityEstablishment


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

    def __init__(
        self,
        form_id='id-identity-form',
        form_action='/api/v0/identity/identity/',
        subject_field=None,
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
        self.helper.form_action = form_action
        self.helper.form_method = 'post'

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

        if subject_field:
            element_subject_field = Field(
                subject_field,
                id='identity-subject-input'
            )

        else:
            element_subject_field = None

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
                element_subject_field,
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
    class Meta(IdentitySimpleForm.Meta):
        model = IdentityIndividual

    identity_type = IntegerField(
        initial=IdentityTypes.INDIVIDUAL,
        widget=HiddenInput()
    )

    user_id = CharField(
        max_length=36,
        label='',
        widget=HiddenInput
    )

    def __init__(
        self,
        instance=None,
        *args,
        **kwargs
    ):
        if instance is not None:
            form_action = '/api/v0/identity/individual/' + instance.pk + '/'

        else:
            form_action='/api/v0/identity/individual/'

        super(IdentityIndividualSimpleForm, self).__init__(
            form_action=form_action,
            placeholder_text='Your Name',
            subject_field='user_id',
            instance=instance,
            *args,
            **kwargs
        )


class IdentityBusinessSimpleForm(IdentitySimpleForm):
    class Meta(IdentitySimpleForm.Meta):
        model = IdentityBusiness

    identity_type = IntegerField(
        initial=IdentityTypes.BUSINESS,
        widget=HiddenInput()
    )

    individual_id = CharField(
        max_length=36,
        label='',
        widget=HiddenInput
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(IdentityBusinessSimpleForm, self).__init__(
            form_action='/api/v0/identity/business/',
            placeholder_text='Business Name',
            subject_field='individual_id',
            *args,
            **kwargs
        )


class IdentityEstablishmentSimpleForm(IdentitySimpleForm):
    class Meta(IdentitySimpleForm.Meta):
        model = IdentityEstablishment

    identity_type = IntegerField(
        initial=IdentityTypes.ESTABLISHMENT,
        widget=HiddenInput()
    )

    business_id = CharField(
        max_length=36,
        label='',
        widget=HiddenInput
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(IdentityEstablishmentSimpleForm, self).__init__(
            form_action='/api/v0/identity/establishment/',
            placeholder_text='Establishment Name',
            subject_field='business_id',
            *args,
            **kwargs
        )
