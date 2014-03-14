import random
import string
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
from knotis.contrib.transaction.models import Transaction

from knotis.contrib.paypal.views import IPNCallbackView

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
            pk=request.session['current_identity_id']
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
            return self.generate_response({
                'errors': {'no-field': 'Could not find offer'},
                'status': 'ERROR'
            })

        if not offer.available():
            return self.generate_response({
                'errors': {
                    'no-field': 'This offer is no longer available'
                },
                'status': 'ERROR'
            })

        try:
            customer = stripe.Customer.create(
                card=token,
                description=''.join([
                    current_identity.name,
                    ' (',
                    current_identity.pk,
                    ')'
                ])
            )

            StripeCustomer.objects.create(
                identity=current_identity,
                stripe_id=customer.id,
                description=current_identity.name
            )

        except Exception, e:
            logger.exception(e.message)
            customer = None

        if not customer:
            return self.generate_response({
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

            mode = 'stripe'
            for i in range(int(quantity)):
                redemption_code = ''.join(
                    random.choice(
                        string.ascii_uppercase + string.digits
                    ) for _ in range(10)
                )

                transaction_context = '|'.join([
                    current_identity.pk,
                    IPNCallbackView.generate_ipn_hash(current_identity.pk),
                    redemption_code,
                    mode
                ])

                Transaction.objects.create_purchase(
                    offer,
                    current_identity,
                    buyer_usd,
                    transaction_context=transaction_context
                )

        except Exception, e:
            logger.exception(e.message)
            return self.generate_response({
                'status': 'ERROR',
                'errors': {'no-field': e.message}
            })

        return self.generate_response({'status': 'OK'})
