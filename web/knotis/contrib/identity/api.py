import json

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse

from knotis.views import ApiView
from knotis.contrib.relation.models import Relation
from models import IdentityIndividual
from forms import IdentitySimpleForm


class IdentityApi(ApiView):
    model = IdentityIndividual
    model_name = 'identity'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        try:
            relation_individual = Relation.objects.get_individual(
                request.user

            )

            individual = relation_individual.related

        except Exception:
            individual = None

        form = IdentitySimpleForm(request.POST, instance=individual)

        errors = {}
        try:
            individual = form.save()

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

        response_data = {}

        if errors:
            response_data['message'] = (
                'An error occurred during identity creation.'
            )
            response_data['errors'] = errors

        else:
            response_data['data'] = {
                'identityid': individual.id,
                'identityname': individual.name
            }
            response_data['message'] = 'Identity created successfully'

        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
