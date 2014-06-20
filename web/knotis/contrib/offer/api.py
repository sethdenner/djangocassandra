from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import (
    ApiView,
    ApiModelViewSet
)

from knotis.contrib.inventory.models import Inventory

from .models import (
    Offer,
    OfferTypes,
    OfferPublish,
    OfferAvailability,
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

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)

from knotis.contrib.product.models import (
    Product,
    ProductTypes
)
from knotis.contrib.endpoint.models import Endpoint, EndpointTypes

from knotis.contrib.auth.api import AuthenticationApi
import random
import string


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

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        update_id = request.DATA.get('id')

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
            data=request.DATA,
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


class OfferApiModelViewSet(ApiModelViewSet):
    api_path = 'offer'
    resource_name = 'offer'

    model = Offer
    serializer_class = OfferSerializer

    http_method_names = ['get', 'options']


class OfferAvailabilityModelViewSet(ApiModelViewSet):
    api_path = 'offers'
    resource_name = 'offers'

    model = OfferAvailability
    queryset = OfferAvailability.objects.filter(available=True)
    serializer_class = OfferAvailabilitySerializer

    http_method_names = ['get', 'options']


class OfferCreateApi(object):

    @staticmethod
    def create_offer(
        dark_offer=False,
        create_business=False,
        *args,
        **kwargs
    ):
        owner_name = kwargs.get('owner')
        try:
            owner_identity = Identity.objects.get(
                name=owner_name,
                identity_type=IdentityTypes.BUSINESS
            )
        except:
            if create_business:

                manager_email = kwargs.get('email')
                if manager_email is None:
                    raise Exception('No Email provided for creating business')

                user, identity, errors = AuthenticationApi.create_user(**{
                    'email': manager_email,
                    'password': ''.join(random.choice(
                        string.printable
                    ) for _ in range(16)),
                    'send_validation': False
                })
                identity.save()

            else:
                logger.exception('Cannot find owner %s' % owner_name)
                raise

        currency_name = kwargs.get('currency')

        try:
            currency = Product.currency.get(currency_name)
        except:
            logger.exception('Cannot find currency %s' % currency_name)
            raise

        price = kwargs.get('price', 0.0)
        value = kwargs.get('value', 0.0)
        title = kwargs.get('title')
        is_physical = kwargs.get('is_physical')
        stock = kwargs.get('stock')
        title = kwargs.get('title')
        description = kwargs.get('description')
        restrictions = kwargs.get('restrictions')

        try:
            product = Product.objects.create(
                product_type=(ProductTypes.CREDIT, ProductTypes.PHYSICAL)[is_physical],
                title=title,
                sku=currency.sku
            )
        except:
            logger.exception('Cannot find currency %s' % currency_name)
            raise

        inventory = Inventory.objects.create_stack_from_product(
            owner_identity,
            product,
            price=value,
            stock=(stock, 0.0)[stock == -1],
            unlimited=(stock == -1),
        )

        split_inventory = Inventory.objects.split(
            inventory,
            owner_identity,
            1
        )

        offer = Offer.objects.create(
            owner=owner_identity,
            title=title,
            restrictions=restrictions,
            description=description,
            start_time=kwargs.get('start_time'),
            end_time=kwargs.get('end_time'),
            stock=(stock, 0.0)[stock == -1],
            unlimited=(stock == -1),
            inventory=[split_inventory],
            discount_factor=price / value,
            offer_type=(OfferTypes.NORMAL, OfferTypes.DARK)[dark_offer]
        )

        offer.save()

        endpoint_current_identity = Endpoint.objects.get(
            endpoint_type=EndpointTypes.IDENTITY,
            identity=owner_identity
        )
        OfferPublish.objects.create(
            endpoint=endpoint_current_identity,
            subject=offer,
            publish_now=True
        )

        print offer
