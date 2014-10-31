import copy
import datetime

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.shortcuts import redirect
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

from knotis.utils.regex import REGEX_UUID

from knotis.utils.email import (
    generate_email,
    generate_validation_key
)
from knotis.contrib.auth.models import KnotisUser

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.contrib.identity.models import (
    Identity,
    IdentityIndividual,
    IdentityEstablishment,
    IdentityTypes
)

from knotis.contrib.layout.views import DefaultBaseView

from knotis.views import (
    EmbeddedView,
    ModalView
)

from forms import (
    CreateUserForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm
)

from models import (
    UserInformation,
    PasswordReset
)

from api import AuthenticationApi

from emails import send_validation_email


class LoginView(ModalView):
    url_patterns = [r'^login/$']
    template_name = 'knotis/auth/login.html'
    view_name = 'login'
    default_parent_view_class = DefaultBaseView

    post_scripts = [
        'knotis/auth/js/login.js'
    ]

    def process_context(self):
        params = {
            'login_form': LoginForm(
                request=self.request,
                data=self.request.POST if self.request.POST else None
            ),
            'header_title': 'Log In',
            'modal_id': 'auth-modal'
        }

        self.context.update(params)

        return super(LoginView, self).process_context()

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        form = LoginForm(
            request=request,
            data=request.POST
        )

        errors = {}

        if not form.is_valid():
            if form.errors:
                for field, messages in form.errors.iteritems():
                    errors[field] = [messages for message in messages]

            non_field_errors = form.non_field_errors()
            if non_field_errors:
                errors['no-field'] = non_field_errors

            # Message user about failed login attempt.
            return self.render_to_response(
                errors=errors
            )

        user = form.get_user()

        django_login(
            request,
            user
        )

        try:
            user_information = UserInformation.objects.get(user=user)
            if not user_information.default_identity_id:
                identity = IdentityIndividual.objects.get_individual(user)
                user_information.default_identity_id = identity.id
                user_information.save()

            else:
                identity = Identity.objects.get(
                    pk=user_information.default_identity_id
                )

            if IdentityTypes.BUSINESS == identity.identity_type:
                establishments = (
                    IdentityEstablishment.objects.get_establishments(
                        identity
                    )
                )
                identity = establishments[0]

                user_information.default_identity_id = identity.id
                user_information.save()

        except Exception, e:
            logout(request)
            logger.exception(e.message)
            errors['no-field'] = e.message
            return self.render_to_response(errors=errors)

        request.session['current_identity'] = identity.id

        if self.response_format == self.RESPONSE_FORMATS.HTML:
            self.response_fromat = self.RESPONSE_FORMATS.REDIRECT
            data = None

        else:
            data = {
                'status': 'OK' if not errors else 'ERROR',
            }
            if errors:
                data['errors'] = errors

            else:
                data['next_url'] = '/'

        return self.render_to_response(data=data, render_template=False)


class SignUpView(ModalView):
    template_name = 'knotis/auth/sign_up.html'
    view_name = 'sign_up'
    default_parent_view_class = DefaultBaseView

    url_patterns = [
        r'^signup/(?P<account_type>[^/]+)*$'
    ]
    post_scripts = [
        'knotis/auth/js/sign_up.js'
    ]

    def process_context(self):
        self.context.update({
            'signup_form': CreateUserForm(request=self.request),
            'header_title': 'Sign Up',
            'modal_id': 'auth-modal'
        })

        return super(SignUpView, self).process_context()

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        user, identity, errors = AuthenticationApi.create_user(
            **dict(request.POST.iteritems())
        )

        data = {}
        if not errors and self.response_format == self.RESPONSE_FORMATS.HTML:
            self.response_fromat = self.RESPONSE_FORMATS.REDIRECT
            data = None

        elif self.RESPONSE_FORMATS.is_ajax(self.response_format):
            if errors:
                data['message'] = (
                    'An error occurred during account creation'
                )

            else:
                data['data'] = {
                    'userid': user.id,
                    'username': user.username
                }
                data['message'] = 'Account created successfully'
                data['status'] = 'OK' if not errors else 'ERROR'
                data['next_url'] = '/'

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )


class SignUpSuccessView(ModalView):
    url_patterns = [r'^auth/signup/success/$']
    template_name = 'knotis/auth/sign_up_success.html'
    view_name = 'sign_up_success'
    default_parent_view_class = DefaultBaseView

    def process_context(self):
        return self.context.update({
            'modal_id': 'auth-modal'
        })


class ForgotPasswordView(ModalView):
    url_patterns = [r'^auth/forgot/$']
    template_name = 'knotis/auth/forgot.html'
    view_name = 'forgot_password'
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'knotis/auth/js/forgot.js'
    ]

    def process_context(self):
        return self.context.update({
            'forgot_form': ForgotPasswordForm(),
            'modal_id': 'auth-modal'
        })


class ForgotPasswordSuccessView(ModalView):
    url_patterns = [r'auth/forgot/success/$']
    template_name = 'knotis/auth/forgot_success.html'
    view_name = 'forgot_password_success'
    default_parent_view_class = DefaultBaseView

    def process_context(self):
        return self.context.update({
            'modal_id': 'auth-modal'
        })


class ResetPasswordView(EmbeddedView):
    url_patterns = [r''.join([
        '^auth/reset/(?P<user_id>',
        REGEX_UUID,
        ')/(?P<password_reset_key>',
        REGEX_UUID,
        ')/$'
    ])]
    post_scripts = [
        'knotis/auth/js/reset.js'
    ]

    template_name = 'knotis/auth/reset.html'
    view_name = 'reset_password'
    default_parent_view_class = DefaultBaseView

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

                try:
                    user_information = UserInformation.objects.get(user=user)
                    if not user_information.default_identity_id:
                        identity = IdentityIndividual.objects.get_individual(
                            user
                        )
                        user_information.default_identity_id = identity.id
                        user_information.save()

                    else:
                        identity = Identity.objects.get(
                            pk=user_information.default_identity_id
                        )

                    # Fuck validation.
                    for endpoint in Endpoint.objects.filter(
                        validated=False,
                        identity=identity,
                        endpoint_type=EndpointTypes.EMAIL,
                    ):
                        endpoint.validated = True
                        endpoint.save()

                    if IdentityTypes.BUSINESS == identity.identity_type:
                        establishments = (
                            IdentityEstablishment.objects.get_establishments(
                                identity
                            )
                        )
                        identity = establishments[0]

                        user_information.default_identity_id = identity.id
                        user_information.save()

                except Exception, e:
                    logout(request)
                    logger.exception(e.message)
                    errors['no-field'] = e.message
                    return self.render_to_response(errors=errors)

                request.session['current_identity'] = identity.id

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

        request = self.context.get('request')

        local_context = copy.copy(self.context)
        local_context.update({
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
        user_identity = IdentityIndividual.objects.get_individual(user)

    except:
        user_identity = None

    if not user_identity:
        return HttpResponseNotFound('Could not get user identity')

    try:
        user_endpoints = Endpoint.objects.filter(
            endpoint_type=EndpointTypes.EMAIL,
            identity=user_identity
        )

    except:
        user_endpoints = None

    if not user_endpoints:
        return HttpResponseNotFound('Could not find email address')

    for endpoint in user_endpoints:
        if (
            endpoint.endpoint_type == EndpointTypes.EMAIL and
            endpoint.value == username
        ):
            endpoint.validation_key = generate_validation_key()
            endpoint.save()

            send_validation_email(
                user,
                endpoint
            )
            break

    return HttpResponse('OK')


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
            redirect_url = '/signup/'
            return redirect(redirect_url)

        else:
            send_new_user_email(authenticated_user.username)
            django_login(
                request,
                authenticated_user
            )

        try:
            user_information = UserInformation.objects.get(
                user=authenticated_user
            )
            if not user_information.default_identity_id:
                identity = IdentityIndividual.objects.get_individual(
                    authenticated_user
                )
                user_information.default_identity_id = identity.id
                user_information.save()

            else:
                identity = Identity.objects.get(
                    pk=user_information.default_identity_id
                )

            request.session['current_identity'] = identity.id

        except Exception, e:
            logout(authenticated_user)
            logger.exception(e.message)
            redirect_url = settings.LOGIN_URL
            raise

    except:
        logger.exception('exception while validating endpoint')

    return redirect(redirect_url)
