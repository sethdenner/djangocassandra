import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404

from knotis.views import AJAXView
from knotis.contrib.identity.models import Identity


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

        stripe.api_key = settings.STRIPE_API_KEY
        token = request.POST['stripeToken']
        ammount = request.POST['chargeAmmount']

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

        except:
            customer = None

        if not customer:
            raise Exception('Failed to create customer')

        try:
            stripe.Charge.create(
                ammount=ammount,
                currency='usd',
                customer=customer.id
            )

            # SAVE TRANSACTION LOG IN OUR DATABASE

        except:
            raise Exception('Failed to charge customer')

        # SAVE CUSTOMER ID IN OUR DATABASE
