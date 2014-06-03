import stripe

from rest_framework.response import Response
from rest_framework.exceptions import (
    APIException
)

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings

from knotis.views import ApiModelViewSet

from knotis.contrib.identity.models import Identity

from .models import StripeCustomer
from .serializers import StripeCustomerSerializer


class StripeApi(object):
    @staticmethod
    def get_stripe_api_key():
        return settings.STRIPE_API_SECRET

    @staticmethod
    def get_purchase_parameters(request):
        token = request.DATA.get('stripeToken')
        amount = request.DATA.get('chargeAmount')
        offer_id = request.DATA.get('offerId')
        quantity = request.DATA.get('quantity')

        return {
            'token': token,
            'amount': float(amount),
            'offer_id': offer_id,
            'quantity': float(quantity)
        }

    @staticmethod
    def update_customer_card(customer_id, card):
        stripe.api_key = StripeApi.get_stripe_api_key()

        customer = stripe.Customer.retrieve(customer_id)
        customer.card = card
        customer.save()
        return customer

    @staticmethod
    def _generate_stripe_customer_description(identity):
        return ''.join([
            identity.name,
            ' (',
            identity.pk,
            ')'
        ])

    @staticmethod
    def create_customer(customer_identity, token=None):
        stripe.api_key = StripeApi.get_stripe_api_key()

        customer = stripe.Customer.create(
            card=token,
            description=StripeApi._generate_stripe_customer_description(
                customer_identity
            )
        )
        StripeCustomer.objects.create(
            identity=customer_identity,
            stripe_id=customer.id,
            description=(
                StripeApi._generate_stripe_customer_description(
                    customer_identity
                )
            )
        )
        return customer

    @staticmethod
    def get_customer(identity):
        stripe.api_key = StripeApi.get_stripe_api_key()

        try:
            stripe_customer = StripeCustomer.objects.get(
                identity=identity
            )

        except StripeCustomer.DoesNotExist:
            stripe_customer = None

        except Exception, e:
            logger.exception(e.message)
            raise

        if stripe_customer:
            try:
                customer = stripe.Customer.retrieve(stripe_customer.stripe_id)

            except Exception, e:
                logger.exception(e.message)
                raise

        else:
            customer = None

        return customer


class StripeCustomerModelViewSet(ApiModelViewSet):
    api_path = 'stripe/customer'
    resource_name = 'customer'

    model = StripeCustomer
    queryset = StripeCustomer.objects.all()
    serializer_class = StripeCustomerSerializer

    def create(
        self,
        request
    ):
        current_identity_pk = request.DATA.get('current_identity')
        try:
            current_identity = Identity.objects.get(pk=current_identity_pk)

        except Exception, e:
            logger.exception(e.message)
            raise self.CurrentIdentityNotFoundException()

        stripe_token = request.DATA.get('stripeToken')
        if not stripe_token:
            raise self.InvalidStripeTokenException()

        try:
            stripe_customer = StripeApi.create_customer(
                current_identity,
                token=stripe_token
            )

        except Exception, e:
            logger.exception(e.message)
            raise

        serializer = StripeCustomerSerializer(stripe_customer)
        return Response(serializer.data)

    def retrieve(
        self,
        request
    ):
        current_identity_pk = request.QUERY_PARAMS.get('current_identity')
        try:
            current_identity = Identity.objects.get(pk=current_identity_pk)

        except Exception, e:
            logger.exception(e.message)
            raise self.CurrentIdentityNotFoundException()

        customer = StripeApi.get_customer(current_identity)

        if customer:
            serializer = StripeCustomerSerializer(customer)
            return Response(serializer.data)

        else:
            return Response({})

    def list(
        self,
        request
    ):
        return self.retrieve(request)

    class InvalidStripeTokenException(APIException):
        status_code = 500
        default_detail = 'The Stripe token provided is invalid.'

    class CurrentIdentityNotFoundException(APIException):
        status_code = 500
        default_detail = 'Could not determine the current identity.'
