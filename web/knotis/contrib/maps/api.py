import json

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse

from knotis.views import ApiView
from knotis.contrib.identity.models import Identity

from forms import GeocompleteForm
from models import (
    Location
)


class LocationApi(ApiView):
    model = Location
    api_url = 'location'

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        import pdb; pdb.set_trace()
        errors = {}

        update_id = request.POST.get('id')
        if update_id:
            try:
                instance = Location.objects.get(pk=update_id)

            except Exception:
                errors['no-field'] = "Could not find location to update"
                return self.generate_response(None, errors)

        else:
            instance = None

        form = GeocompleteForm(
            data=request.POST,
            instance=instance
        )

        related_id = request.POST.get('related_id')
        if related_id:
            related = Identity.objects.get(pk=related_id)

        else:
            related = None

        if form.is_valid():
            try:
                instance = form.save(commit=False)
                instance.save(related=related)
                form.save_m2m()

            except Exception, e:
                logger.exception(
                    'An Exception occurred during location creation'
                )
                errors['no-field'] = e.message

        else:
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

        return self.generate_response(instance, errors)

    @staticmethod
    def generate_response(instance, errors):
        response_data = {}

        if errors:
            response_data['message'] = (
                'An error occurred during identity creation.'
            )
            response_data['errors'] = errors

        else:
            response_data['data'] = {
                'identityid': instance.id,
                'identityname': instance.name
            }
            response_data['message'] = 'Identity created successfully'

        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
