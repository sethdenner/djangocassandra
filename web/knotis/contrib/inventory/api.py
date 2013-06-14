from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import ApiView

from models import Inventory
from forms import (
    InventoryForm,
    InventoryStackFromProductForm
)


class InventoryApi(ApiView):
    model = Inventory
    api_url = 'inventory'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        form = InventoryStackFromProductForm(data=request.POST)

        if form.is_valid():
            try:
                inventory = Inventory.objects.create_stack_from_product(
                    form.cleaned_data.get('provider'),
                    form.cleaned_data.get('product'),
                    form.cleaned_data.get('stock', 0.),
                )

            except Exception, e:
                error_message = 'An error occurred during inventory creation'
                logger.exception(error_message)
                errors['no-field'] = error_message

                return self.generate_response({
                    'message': e.message,
                    'errors': errors
                })

        else:
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_response({
                'message': 'An exception occurred during inventory creation',
                'errors': errors
            })

        return self.generate_response({
            'inventory_id': inventory.id,
            'message': 'Inventory created sucessfully.'
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
            inventory = Inventory.objects.get(pk=update_id)

        except Exception, e:
            error_message = ''.join([
                'Could not find inventory with id <',
                update_id,
                '>.'
            ])
            logger.exception(error_message)
            errors['no-field'] = error_message

            return self.generate_response({
                'message': e.message,
                'errors': errors
            })

        form = InventoryForm(
            data=request.PUT,
            instance=inventory
        )

        if form.is_valid():
            try:
                inventory = form.save()

            except Exception, e:
                error_message = 'An error occurred during inventory update'
                logger.exception(error_message)
                errors['no-field'] = error_message

                return self.generate_response({
                    'message': e.message,
                    'errors': errors
                })

        else:
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_response({
                'message': 'An exception occurred during inventory update',
                'errors': errors
            })

        return self.generate_response({
            'inventory_id': inventory.id,
            'message': 'Inventory updated sucessfully.'
        })
