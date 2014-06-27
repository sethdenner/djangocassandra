from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import (
    ApiView,
    ApiModelViewSet
)

from rest_framework.exceptions import APIException
from rest_framework.response import Response

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.identity.models import IdentityTypes

from knotis.contrib.inventory.models import Inventory

from .models import (
    Offer,
    OfferPublish,
    OfferAvailability
)
from .forms import (
    OfferForm,
    OfferPublishForm,
    OfferWithInventoryForm
)
from .serializers import (
    OfferSerializer,
    OfferAvailabilitySerializer
)


class OfferPublishApiView(ApiView):
    api_path = 'offer/publish'

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        offer_id = request.PUT.get('offer_id', 'None')

        try:
            offer = Offer.objects.get(pk=offer_id)

        except Exception, e:
            error_message = ''.join([
                'Could not find offer with id <',
                offer_id,
                '>.'
            ])
            logger.exception(error_message)
            errors['no-field'] = error_message

            return self.generate_response({
                'message': e.message,
                'errors': errors
            })

        try:
            offer_publish = OfferPublish.objects.filter(
                subject_object_id=offer.id
            )

        except Exception, e:
            error_message = ''.join([
                'Failed to filter offer publications for offer with id <',
                offer_id,
                '>.'
            ])
            logger.exception(error_message)
            errors['no-field'] = error_message

            return self.generate_response({
                'message': e.message,
                'errors': errors
            })

        failed_publish_ids = []
        for p in offer_publish:
            form = OfferPublishForm(
                data=request.PUT,
                instance=p
            )

            try:
                form.save()

            except Exception, e:
                failed_publish_ids.append(p.id)
                error_message = (
                    'An error occurred during offer publication.'
                )
                logger.exception(error_message)
                errors['no-field'] = error_message

        if errors:
            logger.error(''.join([
                'The following OfferPublish objects failed to publish:\n\t',
                '\n\t'.join(failed_publish_ids)
            ]))
            return self.generate_response({
                'message': 'failed',
                'errors': errors
            })

        else:
            return self.generate_response({
                'offer_id': offer.id,
                'message': 'This offer will be published shortly.'
            })


class OfferApiView(ApiView):
    api_path = 'offer/offer'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        form = OfferWithInventoryForm(
            data=request.POST
        )

        if not form.is_valid():
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_response({
                'message': 'Offer form did not validate',
                'errors': errors
            })

        cleaned_data = form.cleaned_data.copy()

        try:
            inventory = []
            for count in range(0, 100):
                key = ''.join([
                    'inventory_',
                    count
                ])
                inventory_id = cleaned_data.pop(key, None)
                if inventory_id:
                    inventory.append(
                        Inventory.objects.get(pk=inventory_id)
                    )

                else:
                    break

        except Exception, e:
            logger.exception(
                'an error occured while collecting inventory for offer.'
            )

            errors['no-field'] = 'Could not find inventory specified.'
            return self.generate_response({
                'message': e.message,
                'errors': errors
            })

        try:
            offer = Offer.objects.create(
                inventory=inventory,
                **cleaned_data
            )

        except Exception, e:
            logger.exception('an error occured while saving offer.')

            errors['no-field'] = 'There was an error saving your offer.'
            return self.generate_response({
                'message': e.message,
                'errors': errors
            })

        return self.generate_response({
            'message': 'offer saved.',
            'data': {
                'offer_id': offer.id
            }
        })


class OfferApiModelViewSet(ApiModelViewSet, GetCurrentIdentityMixin):
    api_path = 'offer'
    resource_name = 'offer'

    model = Offer
    serializer_class = OfferSerializer
    paginate_by = 20
    paginate_by_param = 'count'
    max_paginate_by = 200

    http_method_names = ['get', 'put', 'options']

    def initial(
        self,
        request,
        *args,
        **kwargs
    ):
        super(OfferApiModelViewSet, self).initial(
            request,
            *args,
            **kwargs
        )

        self.get_current_identity(request)

    def get_queryset(self):
        if (
            self.current_identity and
            self.current_identity.identity_type == IdentityTypes.SUPERUSER
        ):
            return self.model.objects.all()

        else:
            return self.model.objects.filter(
                published=True,
                active=True,
                completed=False
            )

    def update(
        self,
        request,
        pk=None,
        *args,
        **kwargs
    ):
        offer = Offer.objects.get(pk=pk)

        if (
            self.current_identity.pk != offer.owner_id and
            self.current_identity.identity_type != IdentityTypes.SUPERUSER
        ):
            raise self.PermissionDeniedException()

        active = offer.active

        form = OfferForm(
            data=request.DATA,
            instance=offer
        )

        offer = form.save()

        if active != offer.active:
            try:
                availability = OfferAvailability.objects.filter(
                    offer=offer
                )
                for a in availability:
                    a.available = offer.active
                    a.save()

            except:
                logger.exception('failed to update offer availability')

        serializer = OfferSerializer(offer)
        return Response(serializer.data)

    class PermissionDeniedException(APIException):
        status_code = 500
        default_detail = (
            'You do not have permission to access or modify this resource.'
        )


class OfferAvailabilityModelViewSet(ApiModelViewSet):
    api_path = 'offers'
    resource_name = 'offers'

    model = OfferAvailability
    queryset = OfferAvailability.objects.filter(available=True)
    serializer_class = OfferAvailabilitySerializer

    http_method_names = ['get', 'options']
