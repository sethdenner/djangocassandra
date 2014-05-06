from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import ApiView

from knotis.contrib.inventory.models import Inventory

from models import (
    Offer,
    OfferPublish,
    OfferAvailability
)
from forms import (
    OfferForm,
    OfferPublishForm,
    OfferWithInventoryForm
)


class OfferPublishApiView(ApiView):
    api_url = 'offer/publish'

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
    api_url = 'offer/offer'

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

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        update_id = request.PUT.get('id')

        try:
            offer = Offer.objects.get(pk=update_id)

        except Exception, e:
            error_message = ''.join([
                'Could not find offer with id <',
                update_id,
                '>.'
            ])
            logger.exception(error_message)
            errors['no-field'] = error_message

            return self.generate_response({
                'message': e.message,
                'errors': errors
            })

        active = offer.active

        form = OfferForm(
            data=request.PUT,
            instance=offer
        )

        if form.is_valid():
            try:
                offer = form.save()

            except Exception, e:
                error_message = 'An error occurred during offer update'
                logger.exception(error_message)
                errors['no-field'] = error_message

                return self.generate_response({
                    'message': e.message,
                    'errors': errors
                })

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

        else:
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_response({
                'message': 'An exception occurred during offer update',
                'errors': errors
            })

        return self.generate_response({
            'offer_id': offer.id,
            'message': 'Offer updated sucessfully.'
        })
