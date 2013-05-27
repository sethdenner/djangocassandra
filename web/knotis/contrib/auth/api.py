import json

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from knotis.views import ApiView

from forms import SignUpForm
from models import KnotisUser


class AuthUserApi(ApiView):
    model = KnotisUser
    model_name = 'user'

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
