import json

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse

from knotis.views import ApiView
from knotis.contrib.auth.models import KnotisUser
from models import (
    Identity,
    IdentityTypes
)
from forms import (
    IdentitySimpleForm,
    IdentityIndividualSimpleForm,
    IdentityBusinessSimpleForm,
    IdentityEstablishmentSimpleForm
)


class IdentityApi(ApiView):
    model = Identity
    model_name = 'identity'

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        identity_type = int(request.POST.get(
            'identity_type',
            IdentityTypes.UNDEFINED
        ))

        update_id = request.POST.get('id')
        if update_id:
            try:
                instance = Identity.objects.get(pk=update_id)

            except Exception:
                errors['no-field'] = "Could not find identity to update"
                return self.generate_response(None, errors)

        else:
            instance = None

        if IdentityTypes.INDIVIDUAL == identity_type:
            form = IdentityIndividualSimpleForm(
                data=request.POST,
                instance=instance
            )

        elif IdentityTypes.BUSINESS == identity_type:
            form = IdentityBusinessSimpleForm(
                data=request.POST,
                instance=instance
            )

        elif IdentityTypes.ESTABLISHMENT == identity_type:
            form = IdentityEstablishmentSimpleForm(
                data=request.POST,
                instance=instance
            )

        else:
            form = IdentitySimpleForm(
                data=request.POST,
                instance=instance
            )

        subject_id = request.POST.get('subject_id')
        if subject_id:
            if identity_type == IdentityTypes.INDIVIDUAL:
                subject = KnotisUser.objects.get(pk=subject_id)

            else:
                subject = Identity.objects.get(pk=subject_id)

        else:
            subject = None

        if form.is_valid():
            try:
                instance = form.save(commit=False)
                instance.save(subject)
                form.save_m2m()

            except Exception, e:
                logger.exception(
                    'An Exception occurred during identity creation'
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
