import json

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
    HttpResponseNotFound
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
    ForgotPasswordForm
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


class ForgotPasswordView(FragmentView):
    template_name = 'knotis/auth/forgot.html'
    view_name = 'forgot_password'

    def process_context(self):
        return self.context.update({
            'forgot_form': ForgotPasswordForm()
        })


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
