import json
import uuid
import datetime
import copy

from django.forms import (
    CharField,
    EmailField,
    BooleanField,
    PasswordInput,
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
from knotis.utils.email import (
    generate_email,
    generate_validation_key
)
from knotis.contrib.auth.models import (
    KnotisUser,
    PasswordReset
)

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.contrib.endpoint.views import send_validation_email

from django.views.generic import View
from knotis.views.mixins import RenderTemplateFragmentMixin

from forms import (
    CreateUserForm,
    LoginForm
)

from knotis.views import FragmentView

class LoginView(View, RenderTemplateFragmentMixin):
    template_name = 'knotis/auth/login.html'
    view_name = 'login'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        request.session.set_test_cookie()
        return render(
            request,
            self.template_name, {
                'login_form': LoginForm()
            }
        )


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
                'signup_form': CreateUserForm()
            }
        )


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

        sign_up_form = CreateUserForm(request.POST)
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
        form = CreateUserForm()
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

        
class KnotisPasswordResetEmailBody(FragmentView):
    template_name = 'knotis/auth/email_forgot_password.html'

    def process_context(self):
        local_context = copy.copy(self.context)

        account_name = 'Fine Bitstrings'
        browser_link = 'http://example.com'
        reset_link = 'http://example.com'
        
        local_context.update({
            'account_name': account_name,
            'browser_link': browser_link,
            'reset_link': reset_link
        })

        return local_context

