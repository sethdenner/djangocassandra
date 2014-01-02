from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import ApiView

from models import Product
from forms import ProductForm


class ProductApi(ApiView):
    model = Product
    api_url = 'product'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        form = ProductForm(data=request.POST)

        if form.is_valid():
            try:
                product = form.save()

            except Exception, e:
                error_message = 'An error occurred during product creation'
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
                'message': 'An exception occurred during product creation',
                'errors': errors
            })

        return self.generate_response({
            'product_id': product.id,
            'message': 'Product created sucessfully.'
        })

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        update_id = request.PUT.get('id')
        if update_id:
            product = Product.objects.get(pk=update_id)

        else:
            product = None

        form = ProductForm(
            data=request.PUT,
            instance=product
        )

        if form.is_valid():
            try:
                product = form.save()

            except Exception, e:
                error_message = 'An error occurred during product update'
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
                'message': 'An exception occurred during product update',
                'errors': errors
            })

        return self.generate_response({
            'product_id': product.id,
            'message': 'Product updated sucessfully.'
        })

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return self.generate_response({})


class CurrencyApi(ApiView):
    model = Product
    api_url = 'currency'
