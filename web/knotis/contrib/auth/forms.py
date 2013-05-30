from django.utils.http import urlquote
from django.contrib.auth.forms import AuthenticationForm
from django.forms import (
    ModelForm,
    CharField,
    EmailField,
    BooleanField,
    PasswordInput,
    HiddenInput,
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

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.contrib.endpoint.views import send_validation_email
from knotis.contrib.identity.models import IdentityIndividual
from knotis.contrib.relation.models import Relation

from models import KnotisUser


class LoginForm(AuthenticationForm):
    username = CharField(
        label='',
        max_length=30,
        required=True
    )
    password = CharField(
        label='',
        widget=PasswordInput,
        required=True
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(LoginForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-login-form'
        self.helper.form_method = 'post'
        self.helper.form_action = '/api/v1/auth/auth/'
        self.helper.layout = Layout(
            Div(
                Field(
                    'username',
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
                    'login',
                    'Login'
                ),
                HTML(
                    '<button class="btn" data-dismiss="modal" '
                    'aria-hidden="true">Cancel</button>'
                ),
                css_class='modal-footer'
            )
        )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        user = self.get_user()
        if user:
            user_identity_relation = Relation.objects.get_individual(
                self.get_user()
            )
            user_identity = user_identity_relation.related
            primary_email = Endpoint.objects.get_primary_endpoint(
                user_identity,
                EndpointTypes.EMAIL
            )

            if not primary_email.validated:
                self.user_cache = None

                # Message user about account deactivation.
                validation_link = ''.join([
                    '<a id="resend_validation_link" ',
                    'href="/auth/resend_validation_email/',
                    urlquote(cleaned_data['username']),
                    '/" >Click here</a> '
                ])

                raise ValidationError(''.join([
                    'This account still needs to be activated. ',
                    validation_link,
                    'to re-send your validation email.'
                ]))

        return cleaned_data


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
    authenticate = BooleanField(
        initial=True,
        widget=HiddenInput()
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
                Field(
                    'authenticate'
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
        if self.instance.pk is None:
            fail_message = 'created'

        else:
            fail_message = 'saved'

        if self.errors:
            raise ValueError(
                'The %s could not be %s because '
                'the data didn\'t validate.' % (
                    self.instance._meta.object_name,
                    fail_message
                )
            )

        user = user_info = individual = email = None
        try:
            user, user_info = KnotisUser.objects.create_user(
                self.cleaned_data['email'],
                self.cleaned_data['password']
            )

            individual = IdentityIndividual.objects.create(
                user
            )

            email = Endpoint.objects.create(
                endpoint_type=EndpointTypes.EMAIL,
                value=user.email,
                identity=individual,
                primary=True
            )

        except:
            rollback = [
                user,
                user_info,
                individual,
                email
            ]

            for item in rollback:
                if item:
                    item.delete()

            raise

        send_validation_email(
            user.id,
            email
        )

        return user, individual
