from django.forms import (
    ModelForm,
    CharField,
    EmailField,
    PasswordInput,
    ValidationError
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

from knotis.contrib.identity.models import (
    IdentityIndividual
)

from models import (
    KnotisUser,
    UserInformation
)


class SignUpForm(ModelForm):
    class Meta:
        model = KnotisUser
        fields = [
            'email',
            'password'
        ]

    email = EmailField(
        label='',
        max_length=254
    )
    password = CharField(
        label='',
        widget=PasswordInput()
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(SignUpForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-signup-form'
        self.helper.form_method = 'post'
        self.helper.form_action = '/api/v1/auth/user/'
        self.helper.layout = Layout(
            Div(
                Field(
                    'email',
                    id='email-input',
                    placeholder='Email Address',
                ),
                Field(
                    'password',
                    id='password-input',
                    placeholder='Password'
                ),
                css_class='modal-body'
            ),
            ButtonHolder(
                Submit(
                    'signup',
                    'Sign Up',
                    css_class='btn btn-primary',
                ),
                HTML(
                    '<button class="btn" data-dismiss="modal" '
                    'aria-hidden="true">Cancel</button>'
                ),
                css_class='modal-footer'
            )
        )

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        """
        email = self.cleaned_data['email'].lower()
        if KnotisUser.objects.filter(email__iexact=email):
            raise ValidationError(
                'Email address is already in use.'
            )
        return email

    def save(
        self,
        commit=True
    ):
        user = super(SignUpForm, self).save(
            commit=False
        )

        user.username = user.email

        identity = IdentityIndividual.objects.create(
            user
        )

        user_info = UserInformation()
        user_info.user = user
        user_info.username = user
        user_info.default_identity = identity

        if commit:
            user.save()
            user_info.save()

        return user, user_info
