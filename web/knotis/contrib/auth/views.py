import json
import uuid
import datetime

from django.forms import (
    CharField,
    EmailField,
    BooleanField,
    PasswordInput,
    CheckboxInput,
    Form,
    ValidationError
)
from django.shortcuts import (
    render,
    redirect
)
from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout
)
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm
)
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound
)
from django.utils.html import strip_tags
from django.utils.http import urlquote
from django.utils.log import logging
logger = logging.getLogger(__name__)
from django.template import Context
from django.template.loader import get_template

from knotis.utils.view import get_standard_template_parameters
from knotis.utils.email import (
    generate_email,
    generate_validation_key
)
from knotis.contrib.auth.models import (
    KnotisUser,
    PasswordReset
)
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)
from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes,
    EndpointEmail
)
from knotis.contrib.content.models import Content
from knotis.contrib.feedback.views import render_feedback_popup

from django.views.generic import View
from knotis.views.mixins import RenderTemplateFragmentMixin

from forms import SignUpForm

class SignUpView(View, RenderTemplateFragmentMixin):
    template_name = 'knotis/auth/sign_up.html'
    view_name = 'sign_up'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return render(
            request,
            self.template_name, {
                'signup_form': SignUpForm()
            }
        )


'''
class SignUpForm(Form):
    first_name = CharField(label='First Name')
    last_name = CharField(label='Last Name')
    email = EmailField(label='Email Address')
    password = CharField(widget=PasswordInput, label='Password')
    business = BooleanField(widget=CheckboxInput, required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs = {
            'class': 'radius-general',
            'placeholder': 'First Name',
            'autofocus': None,
        }

        self.fields['last_name'].widget.attrs = {
            'class': 'radius-general',
            'placeholder': 'Last Name',
        }

        self.fields['email'].widget.attrs = {
            'class': 'radius-general',
            'placeholder': 'Email',
        }

        self.fields['password'].widget.attrs = {
            'class': 'radius-general',
            'placeholder': 'Password',
        }

        self.fields['business'].widget.attrs = {
            'checked': None,
            'value': '1'
        }

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        """
        email = self.cleaned_data['email']
        if KnotisUser.objects.filter(email__iexact=email):
            raise ValidationError(
                'This email address is already in use. '
                'Please supply a different email address.'
            )
        return email

    def create_user(
        self,
        request
    ):
        return KnotisUser.objects.create_user(
            self.cleaned_data['first_name'],
            self.cleaned_data['last_name'],
            self.cleaned_data['email'],
            self.cleaned_data['password'],
        )
'''

def send_validation_email(
    user_id,
    email_endpoint
):
    subject = 'Welcome to Knotis!'
    generate_email(
        'activate',
        subject,
        settings.EMAIL_HOST_USER,
        [email_endpoint.value.value], {
            'user_id': user_id,
            'validation_key': email_endpoint.validation_key,
            'BASE_URL': settings.BASE_URL,
            'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
            'SERVICE_NAME': settings.SERVICE_NAME
        }
    ).send()


def resend_validation_email(
    request,
    username
):
    if request.method.lower() != 'get':
        return HttpResponseBadRequest('Method must be GET')

    try:
        user = KnotisUser.objects.get(username=username)

    except:
        user = None

    if not user:
        return HttpResponseNotFound('Could not find user')

    try:
        user_endpoints = Endpoint.objects.filter(user=user)

    except:
        user_endpoints = None

    if not user_endpoints:
        return HttpResponseNotFound('Could not find email address')

    for endpoint in user_endpoints:
        if (
            endpoint.type == EndpointTypes.EMAIL and
            endpoint.value.value == username
        ):
            endpoint.validation_key = generate_validation_key()
            endpoint.save()

            send_validation_email(
                user.id,
                endpoint
            )
            break

    return HttpResponse('OK')


def sign_up(request):
    if request.method == 'POST':
        response_data = {
            'success': 'no',
        }
        feedback = ''
        error = ''

        sign_up_form = SignUpForm(request.POST)
        user = None
        if sign_up_form.is_valid():
            try:
                user, identity = sign_up_form.create_user(request)

                email = Endpoint.objects.create_endpoint(
                    EndpointTypes.EMAIL,
                    user.username,
                    identity,
                    True
                )

                send_validation_email(
                    user.id,
                    email
                )

                response_data['success'] = 'yes'
                """
                This is a stopgap to not break
                the existing web UI. This code
                should be removed when the UI
                has been modified not to care
                differentiate between different
                users types of users.
                """
                response_data['user'] = 'user'
                feedback = 'Your Knotis account has been created.'

            except Exception as e:
                error = (
                    'There was an error creating your account: ' + e.message
                )

        else:
            error = 'The following fields are invalid: '
            for e in sign_up_form.errors:
                error += strip_tags(e) + '<br/>'

        if error:
            response_data['message'] = error
            return HttpResponse(
                json.dumps(response_data),
                mimetype='application/json'
            )

        html = get_template('finish_registration.html')
        context = Context({
            'settings': settings,
            'feedback': feedback,
            'error': error
        })
        response_data['html'] = html.render(context)

        return HttpResponse(
            json.dumps(response_data),
            mimetype='application/json'
        )

    else:
        form = SignUpForm()
        return render(
            request,
            'sign_up.html', {
                'form': form,
            }
        )


class KnotisAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(KnotisAuthenticationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs = {
            'class': 'radius-general',
            'id': 'email',
            'type': 'text',
            'name': 'username',
            'placeholder': 'Username',
            'autofocus': None
        }

        self.fields['password'].widget.attrs = {
            'class': 'radius-general',
            'id': 'password',
            'type': 'password',
            'name': 'password',
            'placeholder': 'Password',
        }


def login(request):
    def generate_response(data):
        if request.method == 'POST':
            return HttpResponse(
                json.dumps(data),
                content_type='application/json'
            )
        elif request.method == 'GET':
            form = KnotisAuthenticationForm()
            return render(
                request,
                'login.html', {
                    'form': form
                }
            )

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username:
            username = username.lower()

        user = authenticate(
            username=username,
            password=password
        )

        if not user:
            # Message user about failed login attempt.
            return generate_response({
                'success': 'no',
                'message': 'Login failed. Please try again.'
            })

        user_emails = Endpoint.objects.filter(
            endpoint_type=EndpointTypes.EMAIL,
            user=user
        )
        primary_email = None
        for email in user_emails:
            if email.primary or email.value == username:
                primary_email = email

        if not primary_email.validated:
            # Message user about account deactivation.

            validation_link = ''.join([
                '<a id="resend_validation_link" ',
                'href="/auth/resend_validation_email/',
                urlquote(username),
                '/" >Click here</a> '
            ])

            return generate_response({
                'success': 'no',
                'message': ''.join([
                    'This account still needs to be activated. ',
                    validation_link,
                    'to re-send your validation email.'
                ])
            })

        django_login(
            request,
            user
        )

        default_url = '/dashboard/'

        next_url = request.POST.get('next')

        return generate_response({
            'success': 'yes',
            'redirect': next_url if next_url else default_url
        })

    else:
        return generate_response(None)


def logout(request):
    django_logout(request)
    return redirect('/')


def send_new_user_email(username):
    generate_email(
        'newuser',
        'Knotis.com - New User',
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER], {
            'username': username,
            'BASE_URL': settings.BASE_URL,
            'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
            'SERVICE_NAME': settings.SERVICE_NAME
        }
    ).send()


def validate(
    request,
    user_id,
    validation_key
):
    redirect_url = '/'

    try:
        authenticated_user = authenticate(
            user_id=user_id,
            validation_key=validation_key
        )

        if not authenticated_user:
            user = KnotisUser.objects.get(pk=user_id)

            if Endpoint.objects.validate_endpoints(
                validation_key,
                user
            ):
                redirect_url = settings.LOGIN_URL

        else:
            send_new_user_email(authenticated_user.username)
            django_login(
                request,
                authenticated_user
            )

            redirect_url = '/dashboard/'

    except:
        logger.exception('exception while validating endpoint')

    return redirect(redirect_url)


class KnotisPasswordForgotForm(Form):
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

            generate_email(
                'password_forgot',
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


def password_forgot(request):
    template_parameters = get_standard_template_parameters(request)

    if ('post' == request.method.lower()):
        forgot_form = KnotisPasswordForgotForm(request.POST)
        if forgot_form.is_valid():
            if forgot_form.send_reset_instructions():
                template_parameters['feedback'] = (
                    "Instructions on resetting your password have been sent to %s." % (
                        forgot_form.cleaned_data['email'],
                    )
                )

            else:
                template_parameters['feedback'] = (
                    "There was an error sending your instructions. Please try again."
                )

        else:
            template_parameters['feedback'] = \
                "Please enter a valid email address and try again."

        template_parameters['forgot_form'] = forgot_form

    else:
        template_parameters['forgot_form'] = KnotisPasswordForgotForm()

    return render(
        request,
        'password_forgot.html',
        template_parameters
    )


class KnotisPasswordChangeForm(Form):
    old_password = CharField(label='Old Pass', widget=PasswordInput)
    new_password = CharField(label='New Pass', widget=PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super(KnotisPasswordChangeForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise ValidationError('''
                Your old password was entered incorrectly.
                Please enter it again.
            ''')
        return old_password

    def save_password(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()


class KnotisPasswordResetForm(SetPasswordForm):
    pass


def password_reset(
    request,
    validation_key
):
    template_parameters = get_standard_template_parameters(request)

    try:
        password_reset = PasswordReset.objects.get(
            password_reset_key=validation_key
        )
        user = KnotisUser.objects.get(password_reset.endpoint.value)

    except:
        password_reset = None
        user = None

    if user:
        if 'post' == request.method.lower():
            reset_form = KnotisPasswordResetForm(
                user,
                request.POST
            )
            try:
                if reset_form.is_valid():
                    reset_form.save()
                    user = authenticate(
                        username=user.username,
                        password=reset_form.cleaned_data['new_password1']
                    )
                    django_login(
                        request,
                        user
                    )
                    return redirect('/dashboard/')
            except ValidationError:
                template_parameters['feedback'] = \
                    'The passwords you entered are invalid or do not match.'
            except Exception as e:
                raise e

            template_parameters['reset_form'] = reset_form
        else:
            template_parameters['reset_form'] = KnotisPasswordResetForm(user)
    else:
        template_parameters['feedback'] = \
            'There is no password reset request for this URL.'

    return render(
        request,
        'password_reset.html',
        template_parameters
    )


def plans(request):
    template_parameters = get_standard_template_parameters(request)

    content = {}

    content_set = Content.objects.get_template_content('plans')
    for c in content_set:
        content[c.name] = c.value

    template_parameters.update(content)

    return render(
        request,
        'plans.html',
        template_parameters
    )


class UserProfileForm(Form):
    first_name = CharField(max_length=128, label='First Name')
    last_name = CharField(max_length=128, label='Last Name')
    notify_announcements = BooleanField(required=False)
    notify_offers = BooleanField(required=False)
    notify_events = BooleanField(required=False)

    def save_user_profile(
        self,
        request
    ):
        user = KnotisUser.objects.get(pk=request.user.id)
        user.update(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )

        """
        What does this stuff mean and how is it represented
        in the new system?

        if user_profile:
            notify_announcements = self.cleaned_data.get('notify_announcements')
            notify_offers = self.cleaned_data.get('notify_offers')
            notify_events = self.cleaned_data.get('notify_events')
            user_profile.update(
                notify_announcements=notify_announcements if notify_announcements else False,
                notify_offers=notify_offers if notify_offers else False,
                notify_events=notify_events if notify_events else False
            )
        """


class EmailChangeForm(Form):
    email = EmailField(label='New')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            existing_email = Endpoint.objects.get(
                endpoint_type=EndpointTypes.EMAIL,
                value=email
            )

        except:
            existing_email = None

        if existing_email:
            raise ValidationError('That email address is already in use.')

        return email

    def save_email(
        self,
        request
    ):
        new_email = self.cleaned_data['email']

        user = KnotisUser.objects.get(id=request.user.id)
        identity = user.identity_relation.get()
        endpoint = EndpointEmail(
            identity=identity,
            value=new_email
        )
        endpoint.save()
        generate_email(
            'change_email',
            'Knotis - Change Email Address Request',
            settings.EMAIL_HOST_USER,
            [new_email], {
                'user_id': request.user.id,
                'validation_key': endpoint.validation_key,
                'BASE_URL': settings.BASE_URL,
                'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
                'SERVICE_NAME': settings.SERVICE_NAME
            }
        ).send()


@login_required
def profile(request):
    profile_form = None
    email_form = None
    password_form = None

    template_parameters = get_standard_template_parameters(request)

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = KnotisPasswordChangeForm(
                request.user,
                request.POST
            )
            if password_form.is_valid():
                password_form.save_password()
                template_parameters['feedback'] = (
                    'Your password has been updated.'
                )

            else:
                template_parameters['feedback'] = (
                    'There was an error updating your profile.'
                )

        else:
            password_form = KnotisPasswordChangeForm(request.user)

        if  'change_email' in request.POST:
            email_form = EmailChangeForm(request.POST)
            if email_form.is_valid():
                email_form.save_email(request)
                template_parameters['feedback'] = ''.join([
                    'Instructions on how to change your email have been sent to ',
                    email_form.cleaned_data['email'],
                    '.'
                ])

            else:
                template_parameters['feedback'] = (
                    'There was an error updating your profile.'
                )

        else:
            email_form = EmailChangeForm()

        if 'save_profile' in request.POST:
            profile_form = UserProfileForm(request.POST)
            if profile_form.is_valid():
                profile_form.save_user_profile(request)
                template_parameters['feedback'] = (
                    'Your profile was updated successfully.'
                )

            else:
                template_parameters['feedback'] = (
                    'There was an error updating your profile.'
                )

        else:
            user_profile = template_parameters['user_profile']
            profile_form = UserProfileForm({
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'notify_announcements': user_profile.notify_announcements,
                'notify_offers': user_profile.notify_offers,
                'notify_events': user_profile.notify_events
            })

    else:
        user_profile = template_parameters['user_profile']
        profile_form = UserProfileForm({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'notify_announcements': user_profile.notify_announcements,
            'notify_offers': user_profile.notify_offers,
            'notify_events': user_profile.notify_events
        })

        email_form = EmailChangeForm()
        password_form = KnotisPasswordChangeForm(request.user)

    template_parameters['profile_form'] = profile_form
    template_parameters['email_form'] = email_form
    template_parameters['password_form'] = password_form
    template_parameters['user_avatar'] = template_parameters['knotis_user'].avatar(
        request.session.get('fb_id')
    )

    return render(
        request,
        'user_profile.html',
        template_parameters
    )


@login_required
def profile_ajax(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        if not first_name:
            first_name = request.user.first_name

        last_name = request.POST.get('last_name')
        if not last_name:
            last_name = request.user.last_name

        profile_form = UserProfileForm({
            'first_name': first_name,
            'last_name': last_name,
            'notify_announcements': request.POST.get('notify_announcements'),
            'notify_offers': request.POST.get('notify_offers')
        })

        try:
            if profile_form.is_valid():
                profile_form.save_user_profile(request)
                feedback = 'Your profile was successfully updated.'

            else:
                feedback = 'Your profile could not be updated (invalid parameters).'

        except:
            feedback = 'There was an error updating your profile.'

    else:
        return HttpResponseBadRequest()

    return HttpResponse(
        render_feedback_popup(
            'Profile Update',
            feedback
        ),
        mimetype='text/html'
    )
