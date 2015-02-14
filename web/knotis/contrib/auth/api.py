from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)

from .emails import send_validation_email

from .forms import (
    CreateUserForm,
    CreateSuperUserForm,
    ForgotPasswordForm
)


class AuthenticationApi(object):
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

        if not errors and send_validation:
            try:
                endpoint = Endpoint.objects.get(
                    identity=identity,
                    endpoint_type=EndpointTypes.EMAIL,
                    primary=True,
                )

                send_validation_email(
                    user,
                    endpoint,
                    next_url=kwargs.get('next', None)
                )

            except Exception, e:
                logger.exception(e.message)

        return user, identity, errors

    @staticmethod
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

    @staticmethod
    def reset_password(
        request,
        *args,
        **kwargs
    ):
        form = ForgotPasswordForm(
            data=request.POST
        )

        if not form.is_valid():
            return

        form.send_reset_instructions()
