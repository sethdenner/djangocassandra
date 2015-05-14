import stripe

from django.conf import settings
from django.shortcuts import get_object_or_404

from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import (
    AJAXView,
    FragmentView
)
from knotis.contrib.identity.models import Identity
from knotis.contrib.product.models import (
    Product,
    CurrencyCodes
)
from knotis.contrib.inventory.models import Inventory
from knotis.contrib.offer.models import Offer
from knotis.contrib.transaction.api import (
    TransactionApi,
    PurchaseMode
)


from models import StripeCustomer
from forms import StripeForm


class StripeButton(FragmentView):
    template_name = 'knotis/stripe/stripe_button.html'
    view_name = 'stripe_button'

    def process_context(self):
        self.context['stripe_form'] = StripeForm(
            parameters=self.context
        )
        return self.context


class StripeCharge(AJAXView):
    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_object_or_404(
            Identity,
            pk=request.session['current_identity']
        )

        stripe.api_key = settings.STRIPE_API_SECRET
        token = request.POST['stripeToken']
        amount = request.POST['chargeAmount']
        offer_id = request.POST['offerId']
        quantity = request.POST['quantity']

        try:
            offer = Offer.objects.get(pk=offer_id)

        except:
            offer = None

        if not offer:
            return self.generate_ajax_response({
                'errors': {'no-field': 'Could not find offer'},
                'status': 'ERROR'
            })

        if not offer.available():
            return self.generate_ajax_response({
                'errors': {
                    'no-field': 'This offer is no longer available'
                },
                'status': 'ERROR'
            })

        try:
            stripe_customer = StripeCustomer.objects.get(
                identity=current_identity
            )

        except StripeCustomer.DoesNotExist:
            stripe_customer = None

        except Exception, e:
            logger.exception(e.message)
            stripe_customer = None

        try:
            if not stripe_customer:
                customer = stripe.Customer.create(
                    card=token,
                    description=''.join([
                        current_identity.name,
                        ' (',
                        str(current_identity.pk),
                        ')'
                    ])
                )

                StripeCustomer.objects.create(
                    identity=current_identity,
                    stripe_id=customer.id,
                    description=current_identity.name
                )

            else:
                customer = stripe.Customer.retrieve(stripe_customer.stripe_id)
                customer.card = token
                customer.save()

        except Exception, e:
            logger.exception(e.message)
            customer = None

        if not customer:
            return self.generate_ajax_response({
                'errors': {'no-field': 'Failed to create customer'},
                'status': 'ERROR'
            })

        try:
            amount = float(amount)
            stripe.Charge.create(
                amount=int(amount * 100.),
                currency='usd',
                customer=customer.id
            )

            usd = Product.currency.get(CurrencyCodes.USD)
            buyer_usd = Inventory.objects.create_stack_from_product(
                current_identity,
                usd,
                stock=amount,
                get_existing=True
            )

            mode = PurchaseMode.STRIPE
            for i in range(int(quantity)):
                TransactionApi.create_purchase(
                    request=request,
                    offer=offer,
                    buyer=current_identity,
                    currency=buyer_usd,
                    mode=mode
                )

        except Exception, e:
            logger.exception(e.message)
            return self.generate_ajax_response({
                'status': 'ERROR',
                'errors': {'no-field': e.message}
            })

        return self.generate_ajax_response({'status': 'OK'})