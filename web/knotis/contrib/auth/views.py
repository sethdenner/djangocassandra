import copy
import json
import datetime

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.shortcuts import (
    render,
    redirect
)
from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout
)
from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect
)
from django.utils.html import strip_tags
from django.template import Context
from django.template.loader import get_template
from knotis.utils.email import (
    generate_email,
    generate_validation_key
)
from knotis.contrib.auth.models import KnotisUser

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.contrib.endpoint.views import send_validation_email

from knotis.views import FragmentView

from forms import (
    CreateUserForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm
)

from models import (
    PasswordReset
)


class LoginView(FragmentView):
    template_name = 'knotis/auth/login.html'
    view_name = 'login'

    def process_context(self):
        self.request.session.set_test_cookie()
        return self.context.update({
            'login_form': LoginForm()
        })


class SignUpView(FragmentView):
    template_name = 'knotis/auth/sign_up.html'
    view_name = 'sign_up'

    def process_context(self):
        return self.context.update({
            'signup_form': CreateUserForm()
        })


class SignUpSuccessView(FragmentView):
    template_name = 'knotis/auth/sign_up_success.html'
    view_name = 'sign_up_success'


class ForgotPasswordView(FragmentView):
    template_name = 'knotis/auth/forgot.html'
    view_name = 'forgot_password'

    def process_context(self):
        return self.context.update({
            'forgot_form': ForgotPasswordForm()
        })


class ForgotPasswordSuccessView(FragmentView):
    template_name = 'knotis/auth/forgot_success.html'
    view_name = 'forgot_password_success'


class ResetPasswordView(FragmentView):
    template_name = 'knotis/auth/reset.html'
    view_name = 'reset_password'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')

        return super(ResetPasswordView, self).get(
            request,
            *args,
            **kwargs
        )

    def post(
        self,
        request,
        user_id,
        password_reset_key,
        *args,
        **kwargs
    ):
        errors = {}
        is_expired = False

        user_id = self.context.get('user_id')
        try:
            user = KnotisUser.objects.get(pk=user_id)

        except:
            user = None

        password_reset_key = self.context.get('password_reset_key')

        try:
            reset = PasswordReset.objects.get(
                user=user,
                password_reset_key=password_reset_key
            )

        except PasswordReset.DoesNotExist:
            reset = None  # no reset object

        except:
            logger.exception('error getting password reset object')
            reset = None

        if reset and datetime.datetime.utcnow() > reset.expires:
            is_expired = True
            reset = None

        if not reset:
            self.context['is_expired'] = is_expired
            self.context['is_reset_valid'] = False

            return HttpResponse(self.render_template_fragment(
                self.context
            ))

        form = ResetPasswordForm(
            user,
            request=request,
            data=request.POST
        )

        if not form.is_valid():
            if form.errors:
                for field, messages in form.errors.iteritems():
                    errors[field] = [messages for message in messages]

            non_field_errors = form.non_field_errors()
            if non_field_errors:
                errors['no-field'] = non_field_errors

            self.context['errors'] = errors
            self.context['reset_form'] = form
            return HttpResponse(self.render_template_fragment(
                self.context
            ))

        form.save()

        user = authenticate(
            username=user.username,
            password=form.cleaned_data.get('new_password1')
        )

        if user is not None:
            if user.is_active:
                django_login(request, user)

            else:
                errors['no-field'] = (
                    'Could not authenticate user. ',
                    'User is inactive.'
                )

        else:
            errors['no-field'] = (
                'User authentication failed.'
            )

        if not errors:
            return HttpResponseRedirect('/')

        else:
            return HttpResponse(self.render_template_fragment(
                self.context
            ))

    def process_context(self):
        user_id = self.context.get('user_id')
        user = KnotisUser.objects.get(pk=user_id)

        password_reset_key = self.context.get('password_reset_key')

        is_expired = False

        try:
            reset = PasswordReset.objects.get(
                user=user,
                password_reset_key=password_reset_key
            )

        except PasswordReset.DoesNotExist:
            reset = None  # no reset object

        except:
            logger.exception('error getting password reset object')
            reset = None

        if reset and datetime.datetime.utcnow() > reset.expires:
            is_expired = True
            reset.delete()
            reset = None

        styles = self.context.get('styles', [])
        post_scripts = self.context.get('post_scripts', [])

        my_styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css'
        ]

        for style in my_styles:
            if not style in styles:
                styles.append(style)

        my_post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'knotis/auth/js/reset.js'
        ]

        for script in my_post_scripts:
            if not script in post_scripts:
                post_scripts.append(script)

        request = self.context.get('request')

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'post_scripts': post_scripts,
            'reset_form': ResetPasswordForm(
                user,
                request=request,
                parameters={
                    'user_id': user_id,
                    'password_reset_key': self.context.get(
                        'password_reset_key'
                    ),
                    'is_reset_valid': reset is not None,
                    'is_expired': is_expired
                }
            )
        })
        return local_context


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
