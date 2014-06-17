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

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.product.models import CurrencyCodes

from .models import StripeCustomer
from .serializers import StripeCustomerSerializer


class StripeApi(object):
    @staticmethod
    def get_stripe_api_key():
        return settings.STRIPE_API_SECRET

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

        existing = StripeApi.get_customer(customer_identity)
        if existing:
            existing = StripeApi.update_customer_card(existing, token)
            return existing

        customer = stripe.Customer.create(
            card=token,
            description=StripeApi._generate_stripe_customer_description(
                customer_identity
            )
        )

        if not customer or not customer.id:
            return None

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
                stripe_customer.customer = customer

            except Exception, e:
                logger.exception(e.message)
                raise

        return customer


class StripeCustomerModelViewSet(ApiModelViewSet, GetCurrentIdentityMixin):
    api_path = 'stripe/customer'
    resource_name = 'customer'

    model = StripeCustomer
    queryset = StripeCustomer.objects.all()
    serializer_class = StripeCustomerSerializer

    allowed_methods = ['GET', 'POST', 'PUT', 'OPTIONS']

    def initial(
        self,
        request,
        *args,
        **kwargs
    ):
        super(StripeCustomerModelViewSet, self).initial(
            request,
            *args,
            **kwargs
        )

        self.get_current_identity(request)

    def create(
        self,
        request
    ):
        if not self.current_identity:
            raise self.CurrentIdentityNotFoundException()

        stripe_token = request.DATA.get('stripeToken')
        if not stripe_token:
            raise self.InvalidStripeTokenException()

        try:
            stripe_customer = StripeApi.create_customer(
                self.current_identity,
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

        if not self.current_identity or self.current_identity.pk != pk:
            raise self.CurrentIdentityNotFoundException()

        try:
            customer = StripeApi.get_customer(self.current_identity)

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

        if not self.current_identity or self.current_identity.pk != pk:
            raise self.CurrentIdentityNotFoundException()

        try:
            customer = StripeApi.get_customer(self.current_identity)

        except Exception, e:
            logger.exception(e.message)
            raise self.FailedToRetrieveStripeCustomer()

        stripe_token = request.DATA.get('stripeToken')
        if not stripe_token:
            raise self.InvalidStripeTokenException()

        try:
            customer = StripeApi.update_customer_card(
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
