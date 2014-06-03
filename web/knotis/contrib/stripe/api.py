import stripe

from rest_framework.response import Response
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed
)

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings

from knotis.views import ApiModelViewSet

from knotis.contrib.identity.models import Identity
from knotis.contrib.product.models import CurrencyCodes

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
    def create_charge(
        customer,
        amount,
        currency_code=CurrencyCodes.USD,
    ):
        stripe.api_key = StripeApi.get_stripe_api_key()

        if not isinstance(customer, stripe.Customer):
            customer = StripeApi.get_customer(customer)

        charge = stripe.Charge.create(
            amount=int(amount * 100.),
            currency=currency_code,
            customer=customer.stripe_id
        )

        return charge

    @staticmethod
    def update_customer_card(customer, card):
        stripe.api_key = StripeApi.get_stripe_api_key()

        if not isinstance(customer, stripe.Customer):
            customer = stripe.Customer.retrieve(customer)

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

        if not customer or not customer.id:
            return None

        stripe_customer = StripeCustomer.objects.create(
            identity=customer_identity,
            stripe_id=customer.id,
            description=(
                StripeApi._generate_stripe_customer_description(
                    customer_identity
                )
            )
        )
        stripe_customer.customer = customer

        return stripe_customer

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
                stripe_customer.customer = customer

            except Exception, e:
                logger.exception(e.message)
                raise

        return stripe_customer


class StripeCustomerModelViewSet(ApiModelViewSet):
    api_path = 'stripe/customer'
    resource_name = 'customer'

    model = StripeCustomer
    queryset = StripeCustomer.objects.all()
    serializer_class = StripeCustomerSerializer

    allowed_methods = ['GET', 'POST', 'PUT', 'OPTIONS']

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
            raise self.StripeCustomerCreationFailedException()

        serializer = self.serializer_class(stripe_customer)
        return Response(serializer.data)

    def retrieve(
        self,
        request,
        pk=None
    ):
        if not pk:
            raise self.NoIdentityPkProvidedException()

        try:
            current_identity = Identity.objects.get(pk=pk)

        except Exception, e:
            logger.exception(e.message)
            raise self.CurrentIdentityNotFoundException()

        try:
            customer = StripeApi.get_customer(current_identity)

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToRetrieveStripeCustomerException()

        if customer:
            serializer = self.serializer_class(customer)
            return Response(serializer.data)

        else:
            return Response({})

    def update(
        self,
        request,
        pk=None
    ):
        if not pk:
            raise self.NoIdentityPkProvidedException()

        try:
            current_identity = Identity.objects.get(pk=pk)

        except Exception, e:
            logger.exception(e.message)
            raise self.CurrentIdentityNotFoundException()

        try:
            customer = StripeApi.get_customer(current_identity)

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToRetrieveStripeCustomer()

        stripe_token = request.DATA.get('stripeToken')
        if not stripe_token:
            raise self.InvalidStripeTokenException()

        try:
            StripeApi.update_customer_card(
                customer.customer,
                stripe_token
            )

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToUpdateStripeCustomerException()

        serializer = self.serializer_class(customer)
        return Response(serializer.data)

    def list(
        self,
        request
    ):
        raise MethodNotAllowed(request.method)

    class InvalidStripeTokenException(APIException):
        status_code = 500
        default_detail = 'The Stripe token provided is invalid.'

    class NoIdentityPkProvidedException(APIException):
        status_code = 500
        default_detaul = 'No identity pk was provided.'

    class CurrentIdentityNotFoundException(APIException):
        status_code = 500
        default_detail = 'Could not determine the current identity.'

    class FailedToRetrieveStripeCustomerException(APIException):
        status_code = 500
        default_detail = 'Failed to retrieve Stripe customer.'

    class StripeCustomerCreationFailedException(APIException):
        status_code = 500
        default_detail = 'Failed to create Stripe customer.'

    class FailedToUpdateStripeCustomerException(APIException):
        status_code = 500
        default_detail = 'Failed to update Stripe customer.'
