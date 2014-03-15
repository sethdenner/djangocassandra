from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from knotis.views import ApiView

from knotis.contrib.identity.models import (
    Identity,
    IdentityIndividual
)

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)

from forms import (
    LoginForm,
    CreateUserForm,
    CreateSuperUserForm,
    ForgotPasswordForm
)
from models import (
    UserInformation
)
from views import send_validation_email


class AuthenticationApi(ApiView):
    api_url = 'auth/auth'

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
            return self.generate_response({
                'message': 'Login failed. Please try again.',
                'errors': errors
            })

        user = form.get_user()

        login(
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

        except Exception:
            logger.exception('could not get user identity.')
            logout(user)

        request.session['current_identity_id'] = identity.id

        default_url = '/'

        next_url = request.POST.get('next')

        return self.generate_response({
            'success': 'yes',
            'redirect': next_url if next_url else default_url
        })


class AuthUserApi(ApiView):
    api_url = 'auth/user'

    @staticmethod
    def create_user(
        send_validation=True,
        *args,
        **kwargs
    ):
        form = CreateUserForm(data=kwargs)

        errors = {}

        user = identity = None
        try:
            user, identity = form.save()

        except ValueError, e:
            logger.exception(
                'CreateUserForm validation failed'
            )

            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

        except Exception, e:
            errors['no-field'] = e.message
            logger.exception(
                'An Exception occurred during account creation'
            )

        if send_validation:
            try:
                endpoint = Endpoint.objects.get(
                    identity=identity,
                    endpoint_type=EndpointTypes.EMAIL,
                    primary=True,
                )

                send_validation_email(
                    user,
                    endpoint
                )

            except Exception, e:
                logger.exception(e.message)

        return user, identity, errors

    def create_superuser(
        self,
        *args,
        **kwargs
    ):
        form = CreateSuperUserForm(data=kwargs)

        errors = {}

        user = identity = None
        try:
            user, identity = form.save()

        except ValueError, e:
            logger.exception(
                'CreateSuperUserForm validation failed'
            )

            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

        except Exception, e:
            errors['no-field'] = e.message
            logger.exception(
                'An Exception occurred during account creation'
            )

        return user, identity, errors

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        user, identity, errors = self.create_user(
            **dict(request.POST.iteritems())
        )

        if request.POST.get('authenticate', 'false').lower() == 'true':
            user = authenticate(
                username=request.POST.get('username'),
                password=request.POST.get('password')
            )
            if user is not None:
                if user.is_active:
                    login(request, user)

                else:
                    errors['no-field'] = (
                        'Could not authenticate user. ',
                        'User is inactive.'
                    )

            else:
                errors['no-field'] = (
                    'User authentication failed.'
                )

        response_data = {}

        if errors:
            response_data['message'] = (
                'An error occurred during account creation'
            )
            response_data['errors'] = errors

        else:
            response_data['data'] = {
                'userid': user.id,
                'username': user.username
            }
            response_data['message'] = 'Account created successfully'

        return self.generate_response(response_data)


class AuthForgotPasswordApi(ApiView):
    api_url = 'auth/forgot'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        form = ForgotPasswordForm(
            data=request.POST
        )

        errors = {}

        if not form.is_valid():
            pass  # errors

        if not form.send_reset_instructions():
            pass  # errors

        response_data = {}

        if errors:
            response_data = {
                'errors': errors,
                'status': 'ERROR'
            }

        else:
            response_data = {
                'status': 'OK'
            }

        return self.generate_response(response_data)
