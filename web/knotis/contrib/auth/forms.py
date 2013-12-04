import uuid
import datetime

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.utils.http import urlquote
from django.contrib.auth.forms import AuthenticationForm
from django.forms import (
    CharField,
    EmailField,
    BooleanField,
    PasswordInput,
    HiddenInput,
    ValidationError
)

from knotis.forms import (
    TemplateForm,
    TemplateModelForm,
    TemplateFormMixin
)

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.contrib.endpoint.views import send_validation_email
from knotis.contrib.identity.models import (
    IdentityIndividual,
    IdentitySuperUser
)
from knotis.contrib.relation.models import Relation

from models import (
    KnotisUser,
    PasswordReset
)

from emails import PasswordResetEmailBody


class LoginForm(TemplateFormMixin, AuthenticationForm):
    template_name = 'knotis/auth/login_form.html'

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


class CreateUserForm(TemplateModelForm):
    template_name = 'knotis/auth/sign_up_form.html'

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
        required=False,
        initial=False,
        widget=HiddenInput()
    )

    def __init__(
        self,
        authenticate=False,
        *args,
        **kwargs
    ):
        super(CreateUserForm, self).__init__(
            *args,
            **kwargs
        )

        self.fields['authenticate'].initial = authenticate

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
        commit=True,
        is_superuser=False
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

        user = user_info = identity = email = None
        try:
            user, user_info = KnotisUser.objects.create_user(
                self.cleaned_data['email'],
                self.cleaned_data['password'],
                is_superuser
            )

            if user.is_superuser:
                identity = IdentitySuperUser.objects.create(
                    user
                )

            else:
                identity = IdentityIndividual.objects.create(
                    user
                )

            user_info.default_identity_id = identity.id
            user_info.save()

            email = Endpoint.objects.create(
                endpoint_type=EndpointTypes.EMAIL,
                value=user.email,
                identity=identity,
                primary=True
            )

            # create identity endpoint
            Endpoint.objects.create(
                endpoint_type=EndpointTypes.IDENTITY,
                value=identity.name,
                identity=identity
            )

        except:
            rollback = [
                user,
                user_info,
                identity,
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

        return user, identity


class CreateSuperUserForm(CreateUserForm):
    def save(
        self,
        *args,
        **kwargs
    ):
        return super(CreateSuperUserForm, self).save(
            is_superuser=True,
            *args,
            **kwargs
        )


class ForgotPasswordForm(TemplateForm):
    template_name = 'knotis/auth/forgot_form.html'

    email = EmailField()

    def send_reset_instructions(self):
        email = self.cleaned_data['email']

        try:
            user = KnotisUser.objects.get(username=email)
        except:
            user = None

        if not user:
            raise Exception('no user with that email address found')

        try:
            primary_email = Endpoint.objects.get_primary_endpoint(
                user=user,
                endpoint_type=EndpointTypes.EMAIL
            )

        except:
            primary_email = None

        if not primary_email:
            raise Exception('user has no primary email.')

        digest = uuid.uuid4().hex
        key = "%s-%s-%s-%s-%s" % (
            digest[:8],
            digest[8:12],
            digest[12:16],
            digest[16:20],
            digest[20:]
        )

        try:
            PasswordReset.objects.create(
                endpoint=primary_email,
                password_reset_key=key,
                expires=datetime.datetime.utcnow() + datetime.timedelta(
                    minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
                )
            )

            email = PasswordResetEmailBody()
            email.generate_email(
                'Knotis.com - Change Password',
                settings.EMAIL_HOST_USER,
                [email], {
                    'validation_key': key,
                    'BASE_URL': settings.BASE_URL,
                    'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
                    'SERVICE_NAME': settings.SERVICE_NAME
                }
            ).send()
            return True
        except:
            logger.exception('failed to initiate password reset')
            return False
