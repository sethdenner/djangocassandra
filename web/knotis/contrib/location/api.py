from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import ApiView
from knotis.contrib.identity.models import (
    Identity,
    IdentityBusiness,
    IdentityTypes
)

from forms import LocationForm
from models import (
    Location,
    LocationItem
)


class LocationApi(ApiView):
    model = Location
    api_url = 'location'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        update_id = request.POST.get('id')
        if update_id:
            try:
                location = Location.objects.get(pk=update_id)

            except Exception, e:
                errors['no-field'] = "Could not find location to update"
                return self.generate_response({
                    'message': e.message,
                    'errors': errors
                })

        else:
            location = None

        form = LocationForm(
            data=request.POST,
            instance=location
        )

        related_id = request.POST.get('related_id')
        if related_id:
            related = Identity.objects.get(pk=related_id)

        else:
            related = None

        location = None
        if form.is_valid():
            try:
                location = form.save()

            except Exception, e:
                logger.exception(
                    'An Exception occurred during location creation'
                )
                errors['no-field'] = e.message

            if location and related:
                try:
                    LocationItem.objects.create(
                        location=location,
                        related=related
                    )

                except:
                    logger.exception(
                        'An exception occurred during location item creation'
                    )

                if related.identity_type == IdentityTypes.ESTABLISHMENT:
                    business = (
                        IdentityBusiness.objects.get_establishment_parent(
                            related
                        )
                    )
                    try:
                        LocationItem.objects.create(
                            location=location,
                            related=business
                        )

                    except:
                        logger.exception(
                            'An exception occurred during '
                            'location item creation'
                        )

        else:
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

        data = {}
        if not errors:
            data['location_id'] = location.id
            data['location_address'] = location.address
            data['message'] = 'Location saved.'

        else:
            data['errors'] = errors
            data['message'] = 'There was an error while saving location.'

        return self.generate_response(data)
