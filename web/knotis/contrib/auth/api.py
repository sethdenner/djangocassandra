import json

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse
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

from forms import (
    LoginForm,
    SignUpForm
)
from models import (
    KnotisUser,
    UserInformation
)


class AuthenticationApi(ApiView):
    model = KnotisUser
    api_url = 'auth'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        def generate_response(data):
            return HttpResponse(
                json.dumps(data),
                content_type='application/json'
            )

        form = LoginForm(
            request,
            request.POST
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
            return generate_response({
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

        return generate_response({
            'success': 'yes',
            'redirect': next_url if next_url else default_url
        })


class AuthUserApi(ApiView):
    model = KnotisUser
    api_url = 'user'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        form = SignUpForm(request.POST)

        errors = {}

        try:
            user, identity = form.save()

        except ValueError, e:
            logger.exception(
                'SignUpForm validation failed'
            )

            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

        except Exception, e:
            errors['no-field'] = e.message
            logger.exception(
                'An Exception occurred during account creation'
            )

        if request.POST.get('authenticate', 'false').lower == 'true':
            user = authenticate(
                request.POST.get('username'),
                request.POST.get('password')
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

        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
