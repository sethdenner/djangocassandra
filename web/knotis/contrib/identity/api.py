import json

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse

from knotis.views import ApiView
from knotis.contrib.relation.models import Relation
from models import Identity
from forms import IdentityFirstForm


class IdentityApi(ApiView):
    model = Identity

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        form = IdentityFirstForm(request.POST)

        errors = {}

        identity = None
        try:
            identity = form.save()
            Relation.objects.create_individual(
                request.user,
                identity
            )

        except ValueError, e:
            logger.exception(
                'IdentityForm validation failed'
            )

            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

        except Exception, e:
            logger.exception(
                'An Exception occurred during identity creation'
            )
            errors['no-field'] = e.message

            if identity:
                identity.delete()

        response_data = {}

        if errors:
            response_data['message'] = (
                'An error occurred during identity creation.'
            )
            response_data['errors'] = errors

        else:
            response_data['data'] = {
                'identityid': identity.id,
                'identityname': identity.name
            }
            response_data['message'] = 'Identity created successfully'

        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
